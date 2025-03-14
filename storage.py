from typing import Dict, Optional, List
from models import UserProfile, ChatSession

class Storage:
    def __init__(self):
        self.users: Dict[int, UserProfile] = {}
        self.chats: Dict[str, ChatSession] = {}
        self.registration_state: Dict[int, str] = {}

    def get_user(self, user_id: int) -> Optional[UserProfile]:
        return self.users.get(user_id)

    def save_user(self, user: UserProfile) -> None:
        self.users[user.telegram_id] = user

    def get_chat_key(self, user1_id: int, user2_id: int) -> str:
        return f"{min(user1_id, user2_id)}:{max(user1_id, user2_id)}"

    def get_chat(self, user1_id: int, user2_id: int) -> Optional[ChatSession]:
        chat_key = self.get_chat_key(user1_id, user2_id)
        return self.chats.get(chat_key)

    def create_chat(self, user1_id: int, user2_id: int) -> ChatSession:
        chat_key = self.get_chat_key(user1_id, user2_id)
        chat = ChatSession(user1_id=user1_id, user2_id=user2_id)
        self.chats[chat_key] = chat
        return chat

    def get_matches(self, user_id: int) -> List[int]:
        user = self.get_user(user_id)
        if not user:
            return []
        
        matches = []
        for other_id, other_user in self.users.items():
            if other_user and (user_id in other_user.likes and 
                other_id in user.likes and 
                other_id != user_id):
                matches.append(other_id)
        return matches

    def set_registration_state(self, user_id: int, state: str) -> None:
        self.registration_state[user_id] = state

    def get_registration_state(self, user_id: int) -> Optional[str]:
        return self.registration_state.get(user_id)

# Создаем экземпляр Storage
storage = Storage()
