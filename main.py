import logging
from flask import Flask, request
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from config import TELEGRAM_TOKEN, WEBHOOK_URL, WEBHOOK_PATH
from bot_handlers import start, profile, match, chat, handle_message

# Настройка логов
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Инициализация Flask
app = Flask(__name__)

# Инициализация бота
application = Application.builder().token(TELEGRAM_TOKEN).build()

# Регистрация обработчиков
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("profile", profile))
application.add_handler(CommandHandler("match", match))
application.add_handler(CommandHandler("chat", chat))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Обработчик вебхука
@app.route(WEBHOOK_PATH, methods=['POST'])
async def webhook():
    """Обработчик входящих обновлений от Telegram."""
    update = request.get_json()
    await application.update_queue.put(update)
    return "ok"

# Главная страница
@app.route("/")
def home():
    return "Бот работает!"

# Запуск бота
async def setup_webhook():
    """Установка вебхука."""
    await application.bot.set_webhook(url=f"{WEBHOOK_URL}{WEBHOOK_PATH}")
    logger.info(f"Вебхук установлен на {WEBHOOK_URL}{WEBHOOK_PATH}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(setup_webhook())
    app.run(host="0.0.0.0", port=8000)
