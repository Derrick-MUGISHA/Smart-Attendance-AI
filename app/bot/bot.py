import logging
import sys
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
)

from app.bot.handlers.upload import handle_upload
from app.bot.handlers.attendance_flow import (
    attendance_conv_handler,
    confirm_handler,
    review_handler,
    reject_handler
)
from app.bot.handlers.commands import (
    start_command,
    help_command,
    status_command,
    today_command,
    process_command,
    rename_command,
    delete_command
)
from app.config import settings

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
)
logger = logging.getLogger(__name__)


def create_bot():

    app = Application.builder().token(
        settings.TELEGRAM_BOT_TOKEN
    ).build()

    # Commands
    app.add_handler(attendance_conv_handler)
    app.add_handler(confirm_handler)
    app.add_handler(review_handler)
    app.add_handler(reject_handler)
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("today", today_command))
    app.add_handler(CommandHandler("process", process_command))
    app.add_handler(CommandHandler("rename", rename_command))
    app.add_handler(CommandHandler("delete", delete_command))

    # Media handling
    app.add_handler(
        MessageHandler(
            filters.PHOTO | filters.Document.ALL,
            handle_upload
        )
    )

    return app


async def run_bot():
    """Start the bot."""
    application = create_bot()

    try:
        # Test connection and get bot info
        await application.initialize()
        bot_info = await application.bot.get_me()
        logger.info(f"Successfully connected! Bot Name: {bot_info.first_name} (@{bot_info.username})")
        
        # Start polling
        await application.start()
        logger.info("Bot is starting polling...")
        await application.updater.start_polling()
        
        # Run until the application is stopped
        # This keeps the loop running
        import asyncio
        while True:
            await asyncio.sleep(1)
            
    except Exception as e:
        logger.error(f"Failed to start bot: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.critical(f"Unexpected error: {e}", exc_info=True)