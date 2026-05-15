import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes
from flask import Flask, request

from agent import invoke_agent

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
assert TELEGRAM_BOT_TOKEN, "TELEGRAM_BOT_TOKEN is not set in the .env file"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

flask_app = Flask(__name__)

ptb_app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()


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


ptb_app.add_handler(CommandHandler("start", start))
ptb_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))


@flask_app.route(f"/{TELEGRAM_BOT_TOKEN}", methods=["POST"])
def webhook():
    """Receive updates from Telegram and pass them to the bot."""
    import asyncio

    async def process():
        await ptb_app.initialize()
        update = Update.de_json(request.get_json(force=True), ptb_app.bot)
        await ptb_app.process_update(update)

    asyncio.run(process())
    return "ok"


if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=5000)
