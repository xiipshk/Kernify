"""Language selection callback handler."""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from database import get_session
from models import User, Language
from services.user_service import get_or_create_user, update_user_language
from keyboards import get_level_keyboard


async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle language selection from main menu."""
    query = update.callback_query
    await query.answer()

    lang_code = query.data.replace("lang_", "")
    user = query.from_user

    async with get_session() as session:
        db_user = await get_or_create_user(session, user.id, user.username, user.first_name, user.last_name)
        await update_user_language(session, db_user, lang_code)

    lang_names = {
        "python": "Python 🐍",
        "cpp": "C++ ⚡",
        "csharp": "C# 💎",
        "javascript": "JavaScript 🌐",
        "rust": "Rust 🦀",
        "css": "CSS 🎨",
    }
    lang_name = lang_names.get(lang_code, lang_code)

    text = (
        f"✅ Язык изменен на: <b>{lang_name}</b>\n\n"
        "Выбери уровень сложности:"
    )

    await query.edit_message_text(
        text,
        reply_markup=get_level_keyboard(),
        parse_mode="HTML",
    )