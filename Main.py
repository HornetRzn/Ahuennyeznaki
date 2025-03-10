import logging
from flask import Flask, request
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
)
from telegram import __version__ as TG_VER

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"20.0 version of this example, visit https://docs.python-telegram-bot.org/en/v20.0/examples.html"
    )

from config import TELEGRAM_TOKEN, WEBHOOK_URL, WEBHOOK_PATH, PORT, HOST
from bot_handlers import (
    start,
    profile,
    match,
    chat,
    handle_message,
)

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Initialize bot application
application = Application.builder().token(TELEGRAM_TOKEN).build()

# Add handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("profile", profile))
application.add_handler(CommandHandler("match", match))
application.add_handler(CommandHandler("chat", chat))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

@app.route(WEBHOOK_PATH, methods=['POST'])
async def webhook_handler():
    """Handle incoming Telegram updates"""
    if request.method == "POST":
        await application.update_queue.put(
            request.get_json(force=True)
        )
        return "ok"
    return "ok"

@app.route("/")
def home():
    return "Bot is running"

async def init():
    """Initialize the bot application"""
    webhook_url = f"{WEBHOOK_URL}{WEBHOOK_PATH}"
    await application.bot.set_webhook(url=webhook_url)
    await application.initialize()
    await application.start()
    logger.info(f"Webhook set to {webhook_url}")

if __name__ == "__main__":
    # Set the port to 5000 as per Replit guidelines
    app.run(host='0.0.0.0', port=5000, debug=True)
