"""Help command handler."""

from telegram import Update
from telegram.ext import ContextTypes


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
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

    if update.message:
        await update.message.reply_text(text, parse_mode="HTML")
    elif update.callback_query:
        await update.callback_query.edit_message_text(text, parse_mode="HTML")