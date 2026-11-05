"""Main entry point for the Telegram bot."""

import asyncio
import logging
import sys
from contextlib import asynccontextmanager

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters,
    PicklePersistence,
)

from config import settings
from database import init_db, close_db
from handlers import (
    start,
    help_command,
    language_callback,
    level_callback,
    topic_callback,
    practice_callback,
    test_callback,
    ai_chat_callback,
    menu_callback,
    cancel_callback,
    onboarding_conversation,
)
from handlers.ai_chat_callback import handle_ai_message
from handlers.error_handler import error_handler
from keyboards import get_main_menu_keyboard

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: Application):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting bot...")
    await init_db()
    logger.info("Database initialized")
    yield
    # Shutdown
    logger.info("Shutting down bot...")
    await close_db()
    logger.info("Database connections closed")


def create_application() -> Application:
    """Create and configure the bot application."""
    # Use persistence for conversation state
    persistence = PicklePersistence(filepath="bot_persistence.pkl")

    app = (
        Application.builder()
        .token(settings.BOT_TOKEN)
        .persistence(persistence)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )

    # Add conversation handler for onboarding
    app.add_handler(onboarding_conversation)

    # Add command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("menu", menu_callback))
    app.add_handler(CommandHandler("cancel", cancel_callback))

    # Add callback query handlers
    app.add_handler(CallbackQueryHandler(language_callback, pattern="^lang_"))
    app.add_handler(CallbackQueryHandler(level_callback, pattern="^level_"))
    app.add_handler(CallbackQueryHandler(topic_callback, pattern="^topic_"))
    app.add_handler(CallbackQueryHandler(practice_callback, pattern="^practice_"))
    app.add_handler(CallbackQueryHandler(test_callback, pattern="^test_"))
    app.add_handler(CallbackQueryHandler(ai_chat_callback, pattern="^ai_"))
    app.add_handler(CallbackQueryHandler(menu_callback, pattern="^menu_"))
    app.add_handler(CallbackQueryHandler(cancel_callback, pattern="^cancel$"))

    # Add message handler for AI chat (TEXT messages, non-commands)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ai_message))

    # Add error handler
    app.add_error_handler(error_handler)

    return app


async def post_init(app: Application):
    """Post initialization tasks."""
    await app.bot.set_my_commands(
        [
            ("start", "Начать / перезапустить бота"),
            ("help", "Помощь и информация"),
            ("menu", "Главное меню"),
            ("cancel", "Отменить текущее действие"),
        ]
    )
    logger.info("Bot commands set")


async def post_shutdown(app: Application):
    """Post shutdown tasks."""
    logger.info("Bot shutdown complete")


def main():
    """Run the bot."""
    app = create_application()

    try:
        app.run_polling(allowed_updates=["message", "callback_query"])
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.exception(f"Bot crashed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()