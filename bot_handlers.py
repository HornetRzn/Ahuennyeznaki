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
    """Start command handler"""
    user = update.effective_user
    if not user:
        return

    if not storage.get_user(user.id):
        profile = UserProfile(
            telegram_id=user.id,
            username=user.username or "",
            first_name=user.first_name
        )
        storage.save_user(profile)
        storage.set_registration_state(user.id, "AWAITING_AGE")
        await update.message.reply_text(
            "Welcome to Dating Bot! Let's create your profile.\n"
            "Please enter your age:"
        )
    else:
        await update.message.reply_text(
            "Welcome back! Use /profile to view your profile or /match to start matching!"
        )

async def handle_registration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the registration process"""
    user_id = update.effective_user.id
    state = storage.get_registration_state(user_id)
    message = update.message.text
    profile = storage.get_user(user_id)

    if not profile or not state:
        return

    if state == "AWAITING_AGE":
        try:
            age = int(message)
            if not 18 <= age <= 100:
                raise ValueError
            profile.age = age
            storage.save_user(profile)
            storage.set_registration_state(user_id, "AWAITING_GENDER")
            await update.message.reply_text(
                "Please select your gender:",
                reply_markup=GENDER_KEYBOARD
            )
        except ValueError:
            await update.message.reply_text("Please enter a valid age (18-100):")

    elif state == "AWAITING_GENDER":
        if message in ["Male", "Female", "Other"]:
            profile.gender = message
            storage.save_user(profile)
            storage.set_registration_state(user_id, "AWAITING_LOOKING_FOR")
            await update.message.reply_text(
                "What are you looking for?",
                reply_markup=LOOKING_FOR_KEYBOARD
            )
        else:
            await update.message.reply_text("Please select a valid gender option.")

    elif state == "AWAITING_LOOKING_FOR":
        if message in ["Men", "Women", "Everyone"]:
            profile.looking_for = message
            storage.save_user(profile)
            storage.set_registration_state(user_id, "AWAITING_BIO")
            await update.message.reply_text("Please write a short bio about yourself:")
        else:
            await update.message.reply_text("Please select a valid option.")

    elif state == "AWAITING_BIO":
        profile.bio = message
        profile.registration_complete = True
        storage.save_user(profile)
        storage.set_registration_state(user_id, None)
        await update.message.reply_text(
            "Registration complete! Use /profile to view your profile or /match to start matching!"
        )

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the profile command"""
    user = storage.get_user(update.effective_user.id)
    if not user:
        await update.message.reply_text("Please use /start to create your profile first!")
        return

    profile_text = (
        f"Your Profile:\n"
        f"Name: {user.first_name}\n"
        f"Age: {user.age}\n"
        f"Gender: {user.gender}\n"
        f"Looking for: {user.looking_for}\n"
        f"Bio: {user.bio}\n"
    )
    await update.message.reply_text(profile_text)

async def match(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the match command"""
    user_id = update.effective_user.id
    user = storage.get_user(user_id)

    if not user or not user.registration_complete:
        await update.message.reply_text("Please complete your profile first!")
        return

    # Find potential match
    for other_id, other_user in storage.users.items():
        if (other_id != user_id and 
            other_id not in user.likes and 
            other_id not in user.dislikes):
            profile_text = (
                f"Name: {other_user.first_name}\n"
                f"Age: {other_user.age}\n"
                f"Gender: {other_user.gender}\n"
                f"Bio: {other_user.bio}\n"
            )
            keyboard = ReplyKeyboardMarkup([
                ['ð Like', 'ð Dislike']
            ], one_time_keyboard=True)
            context.user_data['current_match'] = other_id
            await update.message.reply_text(profile_text, reply_markup=keyboard)
            return

    await update.message.reply_text("No more profiles to show right now!")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the chat command"""
    user_id = update.effective_user.id
    matches = storage.get_matches(user_id)

    if not matches:
        await update.message.reply_text("No matches yet! Use /match to find someone!")
        return

    keyboard = [[str(match_id)] for match_id in matches]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text("Select a match to chat with:", reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle non-command messages"""
    user_id = update.effective_user.id

    # Handle registration process
    if storage.get_registration_state(user_id):
        await handle_registration(update, context)
        return

    # Handle like/dislike
    if update.message.text in ['ð Like', 'ð Dislike']:
        await handle_like_dislike(update, context)
        return

    # Handle chat messages
    try:
        other_id = int(update.message.text)
        if other_id in storage.get_matches(user_id):
            chat = storage.get_chat(user_id, other_id) or storage.create_chat(user_id, other_id)

            if chat.message_count >= MAX_CHAT_MESSAGES:
                other_user = storage.get_user(other_id)
                if other_user and other_user.username:
                    await update.message.reply_text(
                        f"You've reached the message limit! Here's their contact: @{other_user.username}"
                    )
                else:
                    await update.message.reply_text(
                        "You've reached the message limit but the other user doesn't have a username set."
                    )
                return

            chat.messages.append({
                'from_id': user_id,
                'text': update.message.text,
                'timestamp': update.message.date.isoformat()
            })
            chat.message_count += 1

            await update.message.reply_text(
                f"Message sent! ({chat.message_count}/{MAX_CHAT_MESSAGES} messages used)"
            )
    except ValueError:
        await update.message.reply_text("Please use the available commands or reply to chat messages.")

async def handle_like_dislike(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle like/dislike responses"""
    user_id = update.effective_user.id
    user = storage.get_user(user_id)
    other_id = context.user_data.get('current_match')

    if not other_id:
        await update.message.reply_text("Please use /match to start matching!")
        return

    if update.message.text.startswith('ð'):
        user.likes.append(other_id)
        if user_id in storage.get_user(other_id).likes:
            await update.message.reply_text("It's a match! Use /chat to start chatting!")
    else:
        user.dislikes.append(other_id)

    storage.save_user(user)
    context.user_data['current_match'] = None
    await match(update, context)
