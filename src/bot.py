import os
import logging
import requests
from dotenv import load_dotenv
from flask import Flask, request as flask_request

from agent import invoke_agent

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
assert TELEGRAM_BOT_TOKEN, "TELEGRAM_BOT_TOKEN is not set in the .env file"

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

flask_app = Flask(__name__)


def send_message(chat_id: str, text: str):
    """Send a message to a Telegram chat via the Telegram Bot API."""
    requests.post(
        f"{TELEGRAM_API_URL}/sendMessage",
        json={"chat_id": chat_id, "text": text},
    )


@flask_app.route(f"/{TELEGRAM_BOT_TOKEN}", methods=["POST"])
def webhook():
    """Receive updates from Telegram and respond."""
    data = flask_request.get_json(force=True)

    message = data.get("message", {})
    chat_id = str(message.get("chat", {}).get("id", ""))
    text = message.get("text", "")

    if not chat_id or not text:
        return "ok"

    if text == "/start":
        send_message(
            chat_id,
            "Hi! I'm your writing assistant.\n"
            "I can check your spelling and spell words phonetically "
            "using the NATO alphabet.\n"
            "Note: currently I only work in English."
        )
        return "ok"

    logger.info(f"Message from chat_id {chat_id}: {text}")
    response = invoke_agent(text, thread_id=chat_id)
    send_message(chat_id, response)
    return "ok"


if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=5000)
