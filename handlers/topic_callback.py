"""Topic navigation callback handler."""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from database import get_session
from models import User, Topic, Level, Language, Course, TopicStatus, UserProgress
from sqlalchemy import select
from services.user_service import get_or_create_user
from keyboards import get_topics_keyboard, get_topic_detail_keyboard


async def topic_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle topic navigation and selection."""
    query = update.callback_query
    await query.answer()

    data = query.data  # topic_list, topic_{id}, topic_level_{level}, topic_back
    user = query.from_user

    async with get_session() as session:
        db_user = await get_or_create_user(session, user.id, user.username, user.first_name, user.last_name)

        if data == "topic_list":
            # Show topic levels
            await show_topic_levels(query, db_user)
        elif data.startswith("topic_level_"):
            level_str = data.replace("topic_level_", "")
            try:
                level = Level(level_str)
            except ValueError:
                level = Level.BEGINNER
            await show_topics_for_level(query, db_user, level)
        elif data.startswith("topic_"):
            topic_id = int(data.replace("topic_", ""))
            await show_topic_detail(query, db_user, topic_id)
        elif data == "topic_back":
            await show_topic_levels(query, db_user)


async def show_topic_levels(query, db_user: User):
    """Show available levels for the user's language."""
    lang_names = {
        "python": "Python 🐍",
        "cpp": "C++ ⚡",
        "csharp": "C# 💎",
        "javascript": "JavaScript 🌐",
        "rust": "Rust 🦀",
        "css": "CSS 🎨",
    }
    lang_name = lang_names.get(db_user.preferred_language, db_user.preferred_language)

    text = (
        f"📚 <b>Курс: {lang_name}</b>\n\n"
        "Выбери уровень для просмотра тем:"
    )

    await query.edit_message_text(
        text,
        reply_markup=get_topics_keyboard(),
        parse_mode="HTML",
    )


async def show_topics_for_level(query, db_user: User, level: Level):
    """Show topics for a specific level."""
    async with get_session() as session:
        # Get course for user's language
        course_result = await session.execute(
            select(Course).where(Course.language == Language(db_user.preferred_language))
        )
        course = course_result.scalar_one_or_none()

        if not course:
            await query.edit_message_text("❌ Курс не найден")
            return

        # Get topics for this level
        topics_result = await session.execute(
            select(Topic)
            .where(Topic.course_id == course.id, Topic.level == level)
            .order_by(Topic.order)
        )
        topics = topics_result.scalars().all()

        # Get user progress for these topics
        topic_ids = [t.id for t in topics]
        progress_result = await session.execute(
            select(UserProgress.topic_id, UserProgress.status)
            .where(UserProgress.user_id == db_user.id, UserProgress.topic_id.in_(topic_ids))
        )
        progress_map = {pid: status for pid, status in progress_result}

    level_names = {
        Level.BEGINNER: "Начинающий 🌱",
        Level.INTERMEDIATE: "Средний 🌿",
        Level.ADVANCED: "Продвинутый 🌳",
    }

    text = (
        f"📚 <b>Темы: {level_names[level]}</b>\n\n"
        "✅ — освоено  🔄 — в процессе  🔒 — заблокировано\n\n"
        "Выбери тему:"
    )

    await query.edit_message_text(
        text,
        reply_markup=get_topics_keyboard(topics, progress_map, level),
        parse_mode="HTML",
    )


async def show_topic_detail(query, db_user: User, topic_id: int):
    """Show topic detail with actions."""
    async with get_session() as session:
        topic_result = await session.execute(
            select(Topic).where(Topic.id == topic_id)
        )
        topic = topic_result.scalar_one_or_none()

        if not topic:
            await query.edit_message_text("❌ Тема не найдена")
            return

        # Get user progress
        progress_result = await session.execute(
            select(UserProgress).where(
                UserProgress.user_id == db_user.id,
                UserProgress.topic_id == topic_id
            )
        )
        progress = progress_result.scalar_one_or_none()

    status_icons = {
        TopicStatus.MASTERED: "✅",
        TopicStatus.PARTIAL: "🔄",
        TopicStatus.NOT_MASTERED: "❌",
        TopicStatus.UNCLEAR: "❓",
        TopicStatus.UNTESTED: "🔒",
    }
    status_icon = status_icons.get(progress.status if progress else TopicStatus.UNTESTED, "🔒")

    text = (
        f"{status_icon} <b>{topic.title}</b>\n\n"
        f"{topic.description or 'Описание отсутствует'}\n\n"
        f"📝 <b>Содержание:</b>\n{topic.content or 'Контент будет добавлен'}"
    )

    await query.edit_message_text(
        text,
        reply_markup=get_topic_detail_keyboard(topic_id, progress.status if progress else TopicStatus.UNTESTED),
        parse_mode="HTML",
    )