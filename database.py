import asyncpg
from config import DATABASE_URL

class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(DATABASE_URL)

    async def create_tables(self):
        await self.pool.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                username TEXT,
                name TEXT,
                age INT,
                bio TEXT,
                photo TEXT,
                contact_info TEXT
            )
        ''')
        
        await self.pool.execute('''
            CREATE TABLE IF NOT EXISTS matches (
                match_id SERIAL PRIMARY KEY,
                user1_id BIGINT,
                user2_id BIGINT,
                user1_messages INT DEFAULT 0,
                user2_messages INT DEFAULT 0,
                contact_exchanged BOOLEAN DEFAULT FALSE
            )
        ''')
    
    async def add_user(self, user_id, username, name, age, bio, photo):
        # Регистрация пользователя
        pass
    
    async def create_match(self, user1_id, user2_id):
        # Создание мэтча
        pass
    
    async def increment_message_count(self, match_id, is_user1):
        # Обновление счетчика сообщений
        pass
