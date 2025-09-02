import pytest
import aiosqlite
from app.utils.storage import SQLiteStorage
from aiogram.fsm.storage.base import StorageKey

@pytest.mark.asyncio
async def test_set_get_state_and_data(tmp_path):
    # Создаём файл базы для теста
    db_file = tmp_path / "test.db"
    storage = SQLiteStorage(db_path=str(db_file))

    # Создаём таблицу fsm_storage
    async with aiosqlite.connect(db_file) as conn:
        await conn.execute("""
        CREATE TABLE fsm_storage (
            key TEXT PRIMARY KEY,
            state TEXT,
            data TEXT DEFAULT '{}'
        );
        """)
        await conn.commit()

    key = StorageKey(bot_id=1, chat_id=123, user_id=456)

    # Проверка set_state и get_state
    await storage.set_state(key, "test_state")
    state = await storage.get_state(key)
    assert state == "test_state"

    # Проверка set_data и get_data
    data = {"foo": "bar"}
    await storage.set_data(key, data)
    result_data = await storage.get_data(key)
    assert result_data == data

    # Проверка удаления
    await storage.delete_state(key)
    deleted_state = await storage.get_state(key)
    deleted_data = await storage.get_data(key)
    assert deleted_state is None
    assert deleted_data == {}
