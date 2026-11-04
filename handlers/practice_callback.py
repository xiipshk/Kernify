"""Practice tasks callback handler."""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from database import get_session
from models import User, PracticeTask, PracticeSession, Topic, Level
from sqlalchemy import select
from services.user_service import get_or_create_user
from services.practice_service import check_solution, get_hint


async def practice_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle practice task interactions."""
    query = update.callback_query
    await query.answer()

    data = query.data  # practice_list_{topic_id}, practice_{task_id}, practice_submit, practice_hint, practice_next
    user = query.from_user

    async with get_session() as session:
        db_user = await get_or_create_user(session, user.id, user.username, user.first_name, user.last_name)

        if data.startswith("practice_list_"):
            topic_id = int(data.replace("practice_list_", ""))
            await show_practice_list(query, db_user, topic_id, session)
        elif data.startswith("practice_"):
            task_id = int(data.replace("practice_", ""))
            await show_practice_task(query, db_user, task_id, session)
        elif data == "practice_submit":
            # Handle code submission (would need message handler for code)
            await query.edit_message_text(
                "📝 Пришли код сообщением для проверки.\n"
                "Или используй /cancel для отмены."
            )
            context.user_data["awaiting_code"] = True
        elif data.startswith("practice_hint_"):
            task_id = int(data.replace("practice_hint_", ""))
            await show_hint(query, task_id, session)
        elif data.startswith("practice_next_"):
            task_id = int(data.replace("practice_next_", ""))
            await show_next_task(query, db_user, task_id, session)


async def show_practice_list(query, db_user: User, topic_id: int, session):
    """Show list of practice tasks for a topic."""
    tasks_result = await session.execute(
        select(PracticeTask)
        .where(PracticeTask.topic_id == topic_id)
        .order_by(PracticeTask.difficulty, PracticeTask.id)
    )
    tasks = tasks_result.scalars().all()

    # Get user's completed tasks
    from models import PracticeSession
    sessions_result = await session.execute(
        select(PracticeSession.task_id, PracticeSession.status)
        .where(PracticeSession.user_id == db_user.id, PracticeSession.task_id.in_([t.id for t in tasks]))
    )
    session_map = {tid: status for tid, status in sessions_result}

    status_icons = {
        "passed": "✅",
        "failed": "❌",
        "pending": "⏳",
    }

    text = "💻 <b>Практические задачи</b>\n\n"
    for task in tasks:
        icon = status_icons.get(session_map.get(task.id), "⭕")
        text += f"{icon} {task.title} (сложность: {'⭐' * task.difficulty}, XP: {task.xp_reward})\n"

    text += "\nВыбери задачу:"

    keyboard = []
    for task in tasks:
        keyboard.append([InlineKeyboardButton(
            f"{status_icons.get(session_map.get(task.id), '⭕')} {task.title}",
            callback_data=f"practice_{task.id}"
        )])
    keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data=f"topic_{topic_id}")])

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML",
    )


async def show_practice_task(query, db_user: User, task_id: int, session):
    """Show practice task detail."""
    task_result = await session.execute(
        select(PracticeTask).where(PracticeTask.id == task_id)
    )
    task = task_result.scalar_one_or_none()

    if not task:
        await query.edit_message_text("❌ Задача не найдена")
        return

    # Get user's last attempt
    from models import PracticeSession
    session_result = await session.execute(
        select(PracticeSession)
        .where(PracticeSession.user_id == db_user.id, PracticeSession.task_id == task_id)
        .order_by(PracticeSession.created_at.desc())
    )
    last_session = session_result.scalars().first()

    text = (
        f"💻 <b>{task.title}</b>\n\n"
        f"{task.description}\n\n"
        f"📊 Сложность: {'⭐' * task.difficulty}/5\n"
        f"🎁 XP: {task.xp_reward}\n"
    )

    if task.starter_code:
        text += f"\n💡 <b>Начальный код:</b>\n<pre>{task.starter_code}</pre>"

    if last_session:
        status_icon = {"passed": "✅", "failed": "❌", "pending": "⏳"}.get(last_session.status, "⭕")
        text += f"\n\n{status_icon} Последняя попытка: {last_session.status}"
        if last_session.ai_feedback:
            text += f"\n💬 {last_session.ai_feedback[:200]}..."

    keyboard = [
        [InlineKeyboardButton("📝 Решить", callback_data="practice_submit")],
        [InlineKeyboardButton("💡 Подсказка", callback_data=f"practice_hint_{task_id}")],
        [InlineKeyboardButton("◀️ К списку", callback_data=f"practice_list_{task.topic_id}")],
    ]

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML",
    )


async def show_hint(query, task_id: int, session):
    """Show hint for task."""
    task_result = await session.execute(
        select(PracticeTask).where(PracticeTask.id == task_id)
    )
    task = task_result.scalar_one_or_none()

    if not task or not task.hints:
        await query.answer("Подсказок нет", show_alert=True)
        return

    hint = task.hints[0] if task.hints else "Подсказка недоступна"

    await query.answer(f"💡 {hint}", show_alert=True)


async def show_next_task(query, db_user: User, task_id: int, session):
    """Show next task in sequence."""
    # Get current task to find topic
    task_result = await session.execute(
        select(PracticeTask).where(PracticeTask.id == task_id)
    )
    task = task_result.scalar_one_or_none()

    if not task:
        return

    # Find next task
    next_task_result = await session.execute(
        select(PracticeTask)
        .where(PracticeTask.topic_id == task.topic_id, PracticeTask.id > task_id)
        .order_by(PracticeTask.id)
    )
    next_task = next_task_result.scalars().first()

    if next_task:
        await show_practice_task(query, db_user, next_task.id, session)
    else:
        await query.answer("Это последняя задача в теме", show_alert=True)