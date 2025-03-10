import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from models import UserProfile
from storage import storage
from config import MAX_CHAT_MESSAGES

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Keyboard layouts
GENDER_KEYBOARD = ReplyKeyboardMarkup([
    ['Male', 'Female', 'Other']
], one_time_keyboard=True)

LOOKING_FOR_KEYBOARD = ReplyKeyboardMarkup([
    ['Men', 'Women', 'Everyone']
], one_time_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # ... (остальной код без изменений) ...

async def handle_like_dislike(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:  # Перемещено выше!
    """Handle like/dislike responses"""
    user_id = update.effective_user.id
    user = storage.get_user(user_id)
    other_id = context.user_data.get('current_match')

    if not other_id:
        await update.message.reply_text("Please use /match to start matching!")
        return

    if update.message.text.startswith('👍'):
        user.likes.append(other_id)
        if user_id in storage.get_user(other_id).likes:
            await update.message.reply_text("It's a match! Use /chat to start chatting!")
    else:
        user.dislikes.append(other_id)

    storage.save_user(user)
    context.user_data['current_match'] = None
    await match(update, context)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # ... (остальной код без изменений) ...
