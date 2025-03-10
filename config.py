import os

# Токен от @BotFather
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "вставь_свой_токен_здесь")

# Настройки вебхука
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://your-render-service.onrender.com")  # Замени на свой URL
WEBHOOK_PATH = f"/webhook/{TELEGRAM_TOKEN}"

# Лимит сообщений в чате
MAX_CHAT_MESSAGES = 5
