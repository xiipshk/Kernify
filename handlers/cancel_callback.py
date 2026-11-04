"""Cancel callback handler."""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from database import get_session
from models import User
from services.user_service import get_or_create_user
from keyboards import get_main_menu_keyboard
from handlers.start import get_language_display_name, get_level_display_name


async def cancel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle cancel - return to main menu."""
    query = update.callback_query
    if query:
        await query.answer()

    user = update.effective_user or (query.from_user if query else None)
    if not user:
        return

    async with get_session() as session:
        db_user = await get_or_create_user(session, user.id, user.username, user.first_name, user.last_name)

    # Clear any pending state
    context.user_data.clear()

    lang_name = get_language_display_name(db_user.preferred_language)
    level_name = get_level_display_name(db_user.current_level.value)

    text = (
        f"❌ <b>Действие отменено</b>\n\n"
        f"🌐 Язык: {lang_name}\n"
        f"📊 Уровень: {level_name}\n\n"
        "Главное меню:"
    )

    if query:
        await query.edit_message_text(
            text,
            reply_markup=get_main_menu_keyboard(),
            parse_mode="HTML",
        )
    else:
        await update.message.reply_text(
            text,
            reply_markup=get_main_menu_keyboard(),
            parse_mode="HTML",
        )

    return ConversationHandler.END