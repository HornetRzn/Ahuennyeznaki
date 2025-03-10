from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime

@dataclass
class UserProfile:
    telegram_id: int
    username: str
    first_name: str
    bio: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    looking_for: Optional[str] = None
    photos: List[str] = field(default_factory=list)
    likes: List[int] = field(default_factory=list)
    dislikes: List[int] = field(default_factory=list)
    registration_complete: bool = False

@dataclass
class ChatSession:
    user1_id: int
    user2_id: int
    message_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    messages: List[Dict] = field(default_factory=list)
