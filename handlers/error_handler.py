"""Error handler for the bot."""

import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Log errors and notify user if possible."""
    logger.exception(f"Exception while handling update: {context.error}")

    # Try to notify user
    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "❌ Произошла ошибка. Попробуй еще раз или используй /start для перезапуска.",
                parse_mode="HTML",
            )
        except Exception:
            pass  # Ignore errors in error handler