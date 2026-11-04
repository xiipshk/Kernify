"""Level selection callback handler."""

from telegram import Update
from telegram.ext import ContextTypes

from database import get_session
from models import User, Level
from services.user_service import get_or_create_user, update_user_level
from keyboards import get_main_menu_keyboard


async def level_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle level selection."""
    query = update.callback_query
    await query.answer()

    level_str = query.data.replace("level_", "")
    user = query.from_user

    try:
        level = Level(level_str)
    except ValueError:
        level = Level.BEGINNER

    async with get_session() as session:
        db_user = await get_or_create_user(session, user.id, user.username, user.first_name, user.last_name)
        await update_user_level(session, db_user, level)

    level_names = {
        "beginner": "Начинающий 🌱",
        "intermediate": "Средний 🌿",
        "advanced": "Продвинутый 🌳",
    }
    level_name = level_names.get(level.value, level.value)
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
        f"✅ Уровень установлен: <b>{level_name}</b>\n\n"
        f"🌐 Язык: {lang_name}\n"
        f"📊 Уровень: {level_name}\n\n"
        "Главное меню:"
    )

    await query.edit_message_text(
        text,
        reply_markup=get_main_menu_keyboard(),
        parse_mode="HTML",
    )