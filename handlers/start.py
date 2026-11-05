"""Start command handler - entry point and onboarding."""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler, ContextTypes, ConversationHandler

from config import settings
from database import get_session
from models import User, Language, Level, Course
from sqlalchemy import select
from keyboards import get_language_keyboard, get_level_keyboard
from services.user_service import get_or_create_user, update_user_language, update_user_level


# Conversation states for onboarding
SELECT_LANGUAGE, SELECT_LEVEL = range(2)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle /start command - show welcome and start onboarding if needed."""
    user = update.effective_user
    if not user:
        return ConversationHandler.END

    async with get_session() as session:
        db_user = await get_or_create_user(session, user.id, user.username, user.first_name, user.last_name)

        # Check if user has completed onboarding
        if db_user.preferred_language and db_user.current_level:
            # User already onboarded - show main menu
            await show_main_menu(update, context, db_user)
            return ConversationHandler.END

        # Start onboarding - select language
        text = (
            f"👋 Привет, {user.first_name}!\n\n"
            "Добро пожаловать в бот для изучения программирования! 🚀\n\n"
            "Я помогу тебе освоить один из 6 популярных языков:\n"
            "• Python 🐍\n"
            "• C++ ⚡\n"
            "• C# 💎\n"
            "• JavaScript 🌐\n"
            "• Rust 🦀\n"
            "• CSS 🎨\n\n"
            "Выбери язык, с которого хочешь начать:"
        )

        await update.message.reply_text(
            text,
            reply_markup=get_language_keyboard(),
            parse_mode="HTML",
        )

    return SELECT_LANGUAGE


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, db_user: User):
    """Show main menu for onboarded users."""
    from keyboards import get_main_menu_keyboard

    lang_name = get_language_display_name(db_user.preferred_language)
    level_name = get_level_display_name(db_user.current_level.value)

    text = (
        f"🏠 <b>Главное меню</b>\n\n"
        f"👤 <b>Профиль:</b> {update.effective_user.first_name}\n"
        f"🌐 <b>Язык:</b> {lang_name}\n"
        f"📊 <b>Уровень:</b> {level_name}\n\n"
        "Выбери действие:"
    )

    if update.message:
        await update.message.reply_text(
            text,
            reply_markup=get_main_menu_keyboard(),
            parse_mode="HTML",
        )
    elif update.callback_query:
        await update.callback_query.edit_message_text(
            text,
            reply_markup=get_main_menu_keyboard(),
            parse_mode="HTML",
        )


def get_language_display_name(lang_code: str) -> str:
    """Get display name for language code."""
    names = {
        "python": "Python 🐍",
        "cpp": "C++ ⚡",
        "csharp": "C# 💎",
        "javascript": "JavaScript 🌐",
        "rust": "Rust 🦀",
        "css": "CSS 🎨",
    }
    return names.get(lang_code, lang_code)


def get_level_display_name(level: str) -> str:
    """Get display name for level."""
    names = {
        "beginner": "Начинающий 🌱",
        "intermediate": "Средний 🌿",
        "advanced": "Продвинутый 🌳",
    }
    return names.get(level, level)


# Onboarding conversation handlers
async def onboarding_language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle language selection during onboarding."""
    query = update.callback_query
    await query.answer()

    lang_code = query.data.replace("lang_", "")
    user = query.from_user

    async with get_session() as session:
        db_user = await get_or_create_user(session, user.id, user.username, user.first_name, user.last_name)
        await update_user_language(session, db_user, lang_code)

    lang_name = get_language_display_name(lang_code)

    text = (
        f"✅ Отлично! Выбран язык: <b>{lang_name}</b>\n\n"
        "Теперь выбери свой текущий уровень:"
    )

    await query.edit_message_text(
        text,
        reply_markup=get_level_keyboard(),
        parse_mode="HTML",
    )

    return SELECT_LEVEL


async def onboarding_level_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle level selection during onboarding - final step."""
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

    level_name = get_level_display_name(level.value)
    lang_name = get_language_display_name(db_user.preferred_language)

    text = (
        f"🎉 <b>Онбординг завершен!</b>\n\n"
        f"🌐 Язык: {lang_name}\n"
        f"📊 Уровень: {level_name}\n\n"
        "Теперь ты можешь начинать обучение. Используй меню ниже для навигации."
    )

    await query.edit_message_text(
        text,
        reply_markup=None,
        parse_mode="HTML",
    )

    # Show main menu after a moment
    await show_main_menu(update, context, db_user)

    return ConversationHandler.END


async def onboarding_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel onboarding."""
    query = update.callback_query
    if query:
        await query.answer()
        await query.edit_message_text("❌ Онбординг отменен. Используй /start для начала заново.")
    return ConversationHandler.END


# Export conversation handler
from telegram.ext import ConversationHandler as CH

onboarding_conversation = CH(
    entry_points=[],
    states={
        SELECT_LANGUAGE: [CallbackQueryHandler(onboarding_language_callback, pattern="^lang_")],
        SELECT_LEVEL: [CallbackQueryHandler(onboarding_level_callback, pattern="^level_")],
    },
    fallbacks=[CallbackQueryHandler(onboarding_cancel, pattern="^cancel$")],
    name="onboarding",
    persistent=True,
)