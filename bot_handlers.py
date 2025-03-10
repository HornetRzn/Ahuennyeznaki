import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from models import UserProfile
from storage import storage
from config import MAX_CHAT_MESSAGES

# Настройка логов
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Клавиатуры
GENDER_KEYBOARD = ReplyKeyboardMarkup([['Male', 'Female', 'Other']], one_time_keyboard=True)
LOOKING_FOR_KEYBOARD = ReplyKeyboardMarkup([['Men', 'Women', 'Everyone']], one_time_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # ... (код без изменений из предыдущего ответа) ...

async def handle_like_dislike(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # ... (код без изменений из предыдущего ответа) ...

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # ... (код без изменений из предыдущего ответа) ...

# Остальные функции (profile, match, chat) остаются без изменений
