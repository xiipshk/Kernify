"""Test/entrance test callback handler."""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from database import get_session
from models import User, TestQuestion, TestResult, Topic, TopicStatus
from sqlalchemy import select
from services.user_service import get_or_create_user
from services.test_service import evaluate_answer, get_test_questions


async def test_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle entrance test interactions."""
    query = update.callback_query
    await query.answer()

    data = query.data  # test_start_{topic_id}, test_question_{question_id}, test_answer_{question_id}_{score}
    user = query.from_user

    async with get_session() as session:
        db_user = await get_or_create_user(session, user.id, user.username, user.first_name, user.last_name)

        if data.startswith("test_start_"):
            topic_id = int(data.replace("test_start_", ""))
            await start_test(query, db_user, topic_id, session, context)
        elif data.startswith("test_question_"):
            question_id = int(data.replace("test_question_", ""))
            await show_test_question(query, db_user, question_id, session)
        elif data.startswith("test_answer_"):
            parts = data.replace("test_answer_", "").split("_")
            question_id = int(parts[0])
            score = int(parts[1])
            await submit_answer(query, db_user, question_id, score, session, context)
        elif data == "test_finish":
            await finish_test(query, db_user, session, context)


async def start_test(query, db_user: User, topic_id: int, session, context: ContextTypes.DEFAULT_TYPE):
    """Start entrance test for a topic."""
    questions = await get_test_questions(session, topic_id)

    if not questions:
        await query.edit_message_text(
            "❌ Для этой темы пока нет тестовых вопросов.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("◀️ Назад", callback_data=f"topic_{topic_id}")
            ]]),
            parse_mode="HTML",
        )
        return

    # Store test state in context.user_data (persists via PicklePersistence)
    context.user_data["test_state"] = {
        "topic_id": topic_id,
        "question_ids": [q.id for q in questions],
        "current_index": 0,
    }

    await show_test_question(query, db_user, questions[0].id, session)


async def show_test_question(query, db_user: User, question_id: int, session):
    """Show a test question."""
    question_result = await session.execute(
        select(TestQuestion).where(TestQuestion.id == question_id)
    )
    question = question_result.scalar_one_or_none()

    if not question:
        await query.edit_message_text("❌ Вопрос не найден")
        return

    # Check if already answered
    existing_result = await session.execute(
        select(TestResult).where(
            TestResult.user_id == db_user.id,
            TestResult.question_id == question_id
        )
    )
    existing = existing_result.scalar_one_or_none()

    text = (
        f"📝 <b>Входной тест</b>\n\n"
        f"<b>Вопрос:</b> {question.question_text}\n\n"
    )

    if existing:
        text += f"✅ Уже отвечено (оценка: {existing.score}/2)\n\n"

    keyboard = []
    if not existing:
        keyboard.append([
            InlineKeyboardButton("🟢 Полностью понимаю (2)", callback_data=f"test_answer_{question_id}_2"),
            InlineKeyboardButton("🟡 Частично (1)", callback_data=f"test_answer_{question_id}_1"),
        ])
        keyboard.append([
            InlineKeyboardButton("🔴 Не понимаю (0)", callback_data=f"test_answer_{question_id}_0"),
        ])
    else:
        keyboard.append([InlineKeyboardButton("➡️ Следующий", callback_data=f"test_question_next_{question_id}")])

    keyboard.append([InlineKeyboardButton("❌ Завершить тест", callback_data="test_finish")])

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML",
    )


async def submit_answer(query, db_user: User, question_id: int, score: int, session, context: ContextTypes.DEFAULT_TYPE):
    """Submit answer for a test question."""
    # Save result
    result = TestResult(
        user_id=db_user.id,
        question_id=question_id,
        score=score,
        status=TestResult.get_status_from_score(score),
    )
    session.add(result)

    # Update user progress for topic
    question_result = await session.execute(
        select(TestQuestion).where(TestQuestion.id == question_id)
    )
    question = question_result.scalar_one_or_none()

    if question:
        progress_result = await session.execute(
            select(UserProgress).where(
                UserProgress.user_id == db_user.id,
                UserProgress.topic_id == question.topic_id
            )
        )
        progress = progress_result.scalar_one_or_none()

        if not progress:
            progress = UserProgress(
                user_id=db_user.id,
                topic_id=question.topic_id,
                status=TestResult.get_status_from_score(score),
                score=score,
            )
            session.add(progress)
        else:
            progress.status = TestResult.get_status_from_score(score)
            progress.score = score

    await session.commit()

    # Show feedback and next question
    score_text = {2: "🟢 Отлично!", 1: "🟡 Частично", 0: "🔴 Нужно изучить"}
    await query.answer(score_text.get(score, "OK"), show_alert=True)

    # Get next question from context.user_data
    test_state = context.user_data.get("test_state", {})
    test_questions = test_state.get("question_ids", [])
    current_idx = test_state.get("current_index", 0) + 1
    test_state["current_index"] = current_idx
    context.user_data["test_state"] = test_state

    if current_idx < len(test_questions):
        await show_test_question(query, db_user, test_questions[current_idx], session)
    else:
        await finish_test(query, db_user, session, context)


async def finish_test(query, db_user: User, session, context: ContextTypes.DEFAULT_TYPE):
    """Finish test and show results."""
    # Get results only for the current topic being tested
    test_state = context.user_data.get("test_state", {})
    topic_id = test_state.get("topic_id")

    topics = []
    if topic_id:
        topic_result = await session.execute(
            select(Topic).where(Topic.id == topic_id)
        )
        topic = topic_result.scalar_one_or_none()
        topics = [topic] if topic else []

    text = "📊 <b>Результаты теста</b>\n\n"

    for topic in topics:
        questions_result = await session.execute(
            select(TestQuestion).where(TestQuestion.topic_id == topic.id)
        )
        questions = questions_result.scalars().all()

        if not questions:
            continue

        total_score = 0
        max_score = len(questions) * 2

        for q in questions:
            result = await session.execute(
                select(TestResult).where(
                    TestResult.user_id == db_user.id,
                    TestResult.question_id == q.id
                )
            )
            r = result.scalar_one_or_none()
            if r:
                total_score += r.score

        percentage = (total_score / max_score * 100) if max_score > 0 else 0
        status = "✅ Освоено" if percentage >= 70 else "🔄 Требует изучения" if percentage >= 30 else "❌ Не освоено"

        text += f"<b>{topic.title}</b>: {total_score}/{max_score} ({percentage:.0f}%) — {status}\n"

    text += "\nРекомендации будут учтены в твоем плане обучения."

    keyboard = [[InlineKeyboardButton("📚 К темам", callback_data="topic_list")]]

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML",
    )


# Add helper method to TestResult
def get_status_from_score(score: int) -> TopicStatus:
    if score == 2:
        return TopicStatus.MASTERED
    elif score == 1:
        return TopicStatus.PARTIAL
    else:
        return TopicStatus.NOT_MASTERED

TestResult.get_status_from_score = staticmethod(get_status_from_score)