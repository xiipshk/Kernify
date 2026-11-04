"""Main menu callback handler."""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from database import get_session
from models import User
from services.user_service import get_or_create_user
from keyboards import get_main_menu_keyboard


async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle main menu navigation."""
    query = update.callback_query
    await query.answer()

    data = query.data  # menu_course, menu_practice, menu_ai, menu_profile, menu_settings, menu_help
    user = query.from_user

    async with get_session() as session:
        db_user = await get_or_create_user(session, user.id, user.username, user.first_name, user.last_name)

        if data == "menu_course":
            await show_course_menu(query, db_user)
        elif data == "menu_practice":
            await show_practice_menu(query, db_user)
        elif data == "menu_ai":
            await show_ai_menu(query, db_user)
        elif data == "menu_profile":
            await show_profile(query, db_user)
        elif data == "menu_settings":
            await show_settings(query, db_user)
        elif data == "menu_help":
            await show_help(query)
        elif data == "menu_main":
            await show_main_menu(query, db_user)


async def show_main_menu(query, db_user: User):
    """Show main menu."""
    from keyboards import get_main_menu_keyboard
    from handlers.start import get_language_display_name, get_level_display_name

    lang_name = get_language_display_name(db_user.preferred_language)
    level_name = get_level_display_name(db_user.current_level.value)

    text = (
        f"🏠 <b>Главное меню</b>\n\n"
        f"👤 <b>Профиль:</b> {query.from_user.first_name}\n"
        f"🌐 <b>Язык:</b> {lang_name}\n"
        f"📊 <b>Уровень:</b> {level_name}\n\n"
        "Выбери раздел:"
    )

    await query.edit_message_text(
        text,
        reply_markup=get_main_menu_keyboard(),
        parse_mode="HTML",
    )


async def show_course_menu(query, db_user: User):
    """Show course/topics menu."""
    from keyboards import get_course_menu_keyboard
    from handlers.start import get_language_display_name

    lang_name = get_language_display_name(db_user.preferred_language)

    text = (
        f"📚 <b>Курс: {lang_name}</b>\n\n"
        "Выбери действие:"
    )

    await query.edit_message_text(
        text,
        reply_markup=get_course_menu_keyboard(),
        parse_mode="HTML",
    )


async def show_practice_menu(query, db_user: User):
    """Show practice menu."""
    from keyboards import get_practice_menu_keyboard

    text = (
        "💻 <b>Практика</b>\n\n"
        "Решай задачи для закрепления знаний."
    )

    await query.edit_message_text(
        text,
        reply_markup=get_practice_menu_keyboard(),
        parse_mode="HTML",
    )


async def show_ai_menu(query, db_user: User):
    """Show AI tutor menu."""
    from keyboards import get_ai_menu_keyboard

    text = (
        "🤖 <b>ИИ-тьютр</b>\n\n"
        "Задавай вопросы, получай разборы ошибок и объяснения сложных тем."
    )

    await query.edit_message_text(
        text,
        reply_markup=get_ai_menu_keyboard(),
        parse_mode="HTML",
    )


async def show_profile(query, db_user: User):
    """Show user profile with stats."""
    from database import get_session
    from models import UserProgress, PracticeSession, TopicStatus
    from sqlalchemy import select, func

    async with get_session() as session:
        # Get progress stats
        progress_result = await session.execute(
            select(TopicStatus, func.count())
            .select_from(UserProgress)
            .where(UserProgress.user_id == db_user.id)
            .group_by(UserProgress.status)
        )
        progress_stats = dict(progress_result.all())

        # Get practice stats
        practice_result = await session.execute(
            select(func.count(), func.sum(PracticeSession.xp_earned))
            .where(PracticeSession.user_id == db_user.id, PracticeSession.status == "passed")
        )
        solved_count, total_xp = practice_result.first() or (0, 0)

    status_names = {
        TopicStatus.MASTERED: "✅ Освоено",
        TopicStatus.PARTIAL: "🔄 В процессе",
        TopicStatus.NOT_MASTERED: "❌ Не освоено",
        TopicStatus.UNCLEAR: "❓ Неясно",
        TopicStatus.UNTESTED: "🔒 Не проверено",
    }

    text = (
        f"👤 <b>Профиль: {query.from_user.first_name}</b>\n\n"
        f"🌐 Язык: {db_user.preferred_language}\n"
        f"📊 Уровень: {db_user.current_level.value}\n\n"
        f"<b>Прогресс по темам:</b>\n"
    )

    for status, count in progress_stats.items():
        text += f"  {status_names.get(status, status)}: {count}\n"

    text += f"\n💻 Решено задач: {solved_count or 0}\n"
    text += f"⭐ Заработано XP: {total_xp or 0}"

    keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data="menu_main")]]

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML",
    )


async def show_settings(query, db_user: User):
    """Show settings menu."""
    from keyboards import get_settings_keyboard
    from handlers.start import get_language_display_name, get_level_display_name

    lang_name = get_language_display_name(db_user.preferred_language)
    level_name = get_level_display_name(db_user.current_level.value)

    text = (
        f"⚙️ <b>Настройки</b>\n\n"
        f"Текущие:\n"
        f"🌐 Язык: {lang_name}\n"
        f"📊 Уровень: {level_name}\n\n"
        "Что хочешь изменить?"
    )

    await query.edit_message_text(
        text,
        reply_markup=get_settings_keyboard(),
        parse_mode="HTML",
    )


async def show_help(query):
    """Show help from menu."""
    text = (
        "📖 <b>Помощь</b>\n\n"
        "Этот бот поможет тебе выучить программирование на 6 языках:\n"
        "• Python 🐍\n"
        "• C++ ⚡\n"
        "• C# 💎\n"
        "• JavaScript 🌐\n"
        "• Rust 🦀\n"
        "• CSS 🎨\n\n"
        "<b>Основные команды:</b>\n"
        "/start — Начать / перезапустить бота\n"
        "/help — Эта справка\n"
        "/menu — Главное меню\n"
        "/cancel — Отменить текущее действие\n\n"
        "<b>Как учиться:</b>\n"
        "1. Выбери тему в меню «📚 Курс»\n"
        "2. Прочитай теорию\n"
        "3. Пройди входной тест\n"
        "4. Решай практические задачи\n"
        "5. Задавай вопросы ИИ-тьютору\n\n"
        "<b>Особенности:</b>\n"
        "• Адаптивное обучение под твой уровень\n"
        "• Интерактивные тесты с разбором ошибок\n"
        "• Практика с автопроверкой кода\n"
        "• ИИ-тьютр для объяснения сложных тем\n"
        "• Интервальные повторения ошибок\n\n"
        "По вопросам: @support"
    )

    keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data="menu_main")]]

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML",
    )