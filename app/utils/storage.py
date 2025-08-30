import logging
import json
from typing import Optional, Dict, Any

import aiosqlite
from aiogram.fsm.storage.base import BaseStorage, StorageKey, StateType

from app.utils.retry import retry_async


class SQLiteStorage(BaseStorage):
    def __init__(self, db_path="bot.db"):
        self.db_path = db_path

    def _key_to_string(self, key: StorageKey) -> str:
        return f"{key.chat_id}:{key.user_id}"

    def _state_to_string(self, state: Optional[StateType]) -> Optional[str]:
        if state is None:
            return None
        return state.state if hasattr(state, "state") else str(state)

    async def set_state(self, key: StorageKey, state: Optional[StateType]) -> None:
        async def _set():
            key_str = self._key_to_string(key)
            state_str = self._state_to_string(state)
            async with aiosqlite.connect(self.db_path) as conn:
                await conn.execute(
                    """
                    INSERT INTO fsm_storage (key, state, data)
                    VALUES (?, ?, COALESCE((SELECT data FROM fsm_storage WHERE key = ?), '{}'))
                    ON CONFLICT(key) DO UPDATE SET state=excluded.state
                    """,
                    (key_str, state_str, key_str),
                )
                await conn.commit()
            logging.debug(f"State set for {key_str}: {state_str}")
        await retry_async(_set)

    async def get_state(self, key: StorageKey) -> Optional[str]:
        async def _get():
            key_str = self._key_to_string(key)
            async with aiosqlite.connect(self.db_path) as conn:
                cursor = await conn.execute("SELECT state FROM fsm_storage WHERE key=?", (key_str,))
                row = await cursor.fetchone()
                return row[0] if row else None
        return await retry_async(_get)

    async def set_data(self, key: StorageKey, data: Dict[str, Any]) -> None:
        async def _set_data():
            key_str = self._key_to_string(key)
            async with aiosqlite.connect(self.db_path) as conn:
                await conn.execute(
                    """
                    INSERT INTO fsm_storage (key, state, data)
                    VALUES (?, COALESCE((SELECT state FROM fsm_storage WHERE key = ?), NULL), ?)
                    ON CONFLICT(key) DO UPDATE SET data=excluded.data
                    """,
                    (key_str, key_str, json.dumps(data)),
                )
                await conn.commit()
            logging.debug(f"Data set for {key_str}: {data}")
        await retry_async(_set_data)

    async def get_data(self, key: StorageKey) -> Dict[str, Any]:
        async def _get_data():
            key_str = self._key_to_string(key)
            async with aiosqlite.connect(self.db_path) as conn:
                cursor = await conn.execute("SELECT data FROM fsm_storage WHERE key=?", (key_str,))
                row = await cursor.fetchone()
                if row and row[0]:
                    try:
                        return json.loads(row[0])
                    except json.JSONDecodeError:
                        return {}
                return {}
        return await retry_async(_get_data)

    async def delete_state(self, key: StorageKey) -> None:
        async def _delete():
            key_str = self._key_to_string(key)
            async with aiosqlite.connect(self.db_path) as conn:
                await conn.execute("DELETE FROM fsm_storage WHERE key=?", (key_str,))
                await conn.commit()
            logging.debug(f"State deleted for {key_str}")
        await retry_async(_delete)

    async def close(self) -> None:
        pass
