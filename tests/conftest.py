import pytest
from aiogram import Bot
from aiogram import Dispatcher
from unittest.mock import AsyncMock

from app.utils.storage import SQLiteStorage

@pytest.fixture
async def memory_storage():
    storage = SQLiteStorage(db_path=":memory:")
    # Создаём таблицу fsm_storage для in-memory БД
    async with storage._get_conn() as conn:  # или просто aiosqlite.connect(":memory:")
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS fsm_storage (
            key TEXT PRIMARY KEY,
            state TEXT,
            data TEXT DEFAULT '{}'
        );
        """)
        await conn.commit()
    yield storage
    await storage.close()


@pytest.fixture
async def mock_bot():
    bot = AsyncMock(spec=Bot)
    return bot

@pytest.fixture
async def mock_dispatcher(memory_storage):
    dp = Dispatcher(storage=memory_storage)
    yield dp
