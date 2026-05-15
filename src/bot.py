import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

from agent import invoke_agent

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
assert TELEGRAM_BOT_TOKEN, "TELEGRAM_BOT_TOKEN is not set in the .env file"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command."""
    await update.message.reply_text(
        "Hi! I'm your writing assistant.\n"
        "I can check your spelling and spell words phonetically using the NATO alphabet.\n"
        "Note: currently I only work in English."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming user messages, using chat_id as thread_id for memory."""
    chat_id = str(update.message.chat_id)
    user_message = update.message.text

    logger.info(f"Message from chat_id {chat_id}: {user_message}")

    response = invoke_agent(user_message, thread_id=chat_id)
    await update.message.reply_text(response)


def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
