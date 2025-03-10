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
    """Обработчик команды /start."""
    user = update.effective_user
    if not storage.get_user(user.id):
        profile = UserProfile(
            telegram_id=user.id,
            username=user.username or "",
            first_name=user.first_name
        )
        storage.save_user(profile)
        storage.set_registration_state(user.id, "AWAITING_AGE")
        await update.message.reply_text(
            "Привет! Давай создадим твой профиль.\n"
            "Сколько тебе лет?"
        )
    else:
        await update.message.reply_text(
            "С возвращением! Используй /profile для просмотра профиля или /match для поиска."
        )

async def handle_registration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик процесса регистрации."""
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
                "Выбери свой пол:",
                reply_markup=GENDER_KEYBOARD
            )
        except ValueError:
            await update.message.reply_text("Пожалуйста, введи корректный возраст (18-100).")

    elif state == "AWAITING_GENDER":
        if message in ["Male", "Female", "Other"]:
            profile.gender = message
            storage.save_user(profile)
            storage.set_registration_state(user_id, "AWAITING_LOOKING_FOR")
            await update.message.reply_text(
                "Кого ты ищешь?",
                reply_markup=LOOKING_FOR_KEYBOARD
            )
        else:
            await update.message.reply_text("Пожалуйста, выбери корректный пол.")

    elif state == "AWAITING_LOOKING_FOR":
        if message in ["Men", "Women", "Everyone"]:
            profile.looking_for = message
            storage.save_user(profile)
            storage.set_registration_state(user_id, "AWAITING_BIO")
            await update.message.reply_text("Напиши коротко о себе:")
        else:
            await update.message.reply_text("Пожалуйста, выбери корректный вариант.")

    elif state == "AWAITING_BIO":
        profile.bio = message
        profile.registration_complete = True
        storage.save_user(profile)
        storage.set_registration_state(user_id, None)
        await update.message.reply_text(
            "Регистрация завершена! Используй /profile для просмотра профиля или /match для поиска."
        )

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /profile."""
    user = storage.get_user(update.effective_user.id)
    if not user:
        await update.message.reply_text("Пожалуйста, используй /start для создания профиля!")
        return

    profile_text = (
        f"Твой профиль:\n"
        f"Имя: {user.first_name}\n"
        f"Возраст: {user.age}\n"
        f"Пол: {user.gender}\n"
        f"Ищу: {user.looking_for}\n"
        f"О себе: {user.bio}\n"
    )
    await update.message.reply_text(profile_text)

async def match(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /match."""
    user_id = update.effective_user.id
    user = storage.get_user(user_id)

    if not user or not user.registration_complete:
        await update.message.reply_text("Пожалуйста, заверши регистрацию!")
        return

    # Поиск совпадений
    for other_id, other_user in storage.users.items():
        if (other_id != user_id and 
            other_id not in user.likes and 
            other_id not in user.dislikes):
            profile_text = (
                f"Имя: {other_user.first_name}\n"
                f"Возраст: {other_user.age}\n"
                f"Пол: {other_user.gender}\n"
                f"О себе: {other_user.bio}\n"
            )
            keyboard = ReplyKeyboardMarkup([
                ['👍 Like', '👎 Dislike']
            ], one_time_keyboard=True)
            context.user_data['current_match'] = other_id
            await update.message.reply_text(profile_text, reply_markup=keyboard)
            return

    await update.message.reply_text("Сейчас нет доступных анкет!")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /chat."""
    user_id = update.effective_user.id
    matches = storage.get_matches(user_id)

    if not matches:
        await update.message.reply_text("У тебя пока нет совпадений! Используй /match для поиска.")
        return

    keyboard = [[str(match_id)] for match_id in matches]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text("Выбери совпадение для общения:", reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик обычных сообщений."""
    user_id = update.effective_user.id

    # Обработка регистрации
    if storage.get_registration_state(user_id):
        await handle_registration(update, context)
        return

    # Обработка лайков/дизлайков
    if update.message.text in ['👍 Like', '👎 Dislike']:
        await handle_like_dislike(update, context)
        return

    # Обработка сообщений в чате
    try:
        other_id = int(update.message.text)
        if other_id in storage.get_matches(user_id):
            chat = storage.get_chat(user_id, other_id) or storage.create_chat(user_id, other_id)

            if chat.message_count >= MAX_CHAT_MESSAGES:
                other_user = storage.get_user(other_id)
                if other_user and other_user.username:
                    await update.message.reply_text(
                        f"Лимит сообщений исчерпан! Вот контакт: @{other_user.username}"
                    )
                else:
                    await update.message.reply_text(
                        "Лимит сообщений исчерпан, но у пользователя нет username."
                    )
                return

            chat.messages.append({
                'from_id': user_id,
                'text': update.message.text,
                'timestamp': update.message.date.isoformat()
            })
            chat.message_count += 1

            await update.message.reply_text(
                f"Сообщение отправлено! ({chat.message_count}/{MAX_CHAT_MESSAGES} использовано)"
            )
    except ValueError:
        await update.message.reply_text("Пожалуйста, используй доступные команды.")

async def handle_like_dislike(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик лайков и дизлайков."""
    user_id = update.effective_user.id
    user = storage.get_user(user_id)
    other_id = context.user_data.get('current_match')

    if not other_id:
        await update.message.reply_text("Пожалуйста, используй /match для поиска!")
        return

    if update.message.text.startswith('👍'):
        user.likes.append(other_id)
        if user_id in storage.get_user(other_id).likes:
            await update.message.reply_text("Это взаимно! Используй /chat для общения!")
    else:
        user.dislikes.append(other_id)

    storage.save_user(user)
    context.user_data['current_match'] = None
    await match(update, context)
