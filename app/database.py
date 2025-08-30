import asyncio
import logging
from typing import Callable, Any, Tuple, Type, Optional, Dict, List
import aiosqlite

from app.utils.retry import retry_async

async def init_db():
    async def _init():
        async with aiosqlite.connect("bot.db") as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    user_name TEXT,
                    screen_time TEXT,
                    focus TEXT,
                    changes TEXT,
                    feedback TEXT,
                    after_screen_time TEXT,
                    after_focus TEXT,
                    is_useful TEXT,
                    whats_new TEXT,
                    whats_changed TEXT,
                    else_challenge TEXT,
                    topics TEXT
                );
            ''')
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS fsm_storage (
                    key TEXT PRIMARY KEY,
                    state TEXT,
                    data TEXT DEFAULT '{}'
                );
            ''')
            await conn.commit()
        logging.info("База данных инициализирована")
    await retry_async(_init)


async def save_user_data(user_id: int, **fields: Optional[str]) -> None:
    if not fields:
        return

    async def _save():
        async with aiosqlite.connect("bot.db") as conn:
            cursor = await conn.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
            exists = await cursor.fetchone()
            if exists:
                update_fields = [f"{col} = ?" for col in fields.keys()]
                params = list(fields.values()) + [user_id]
                query = f"UPDATE users SET {', '.join(update_fields)} WHERE user_id = ?"
                await conn.execute(query, params)
            else:
                columns = ["user_id"] + list(fields.keys())
                placeholders = ["?"] * len(columns)
                params = [user_id] + list(fields.values())
                query = f"INSERT INTO users ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
                await conn.execute(query, params)
            await conn.commit()
        logging.info(f"Данные пользователя {user_id} обновлены: {fields}")
    await retry_async(_save)

async def get_user_data(user_id: int) -> Optional[Dict[str, Any]]:
    async def _get():
        async with aiosqlite.connect("bot.db") as conn:
            cursor = await conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            row = await cursor.fetchone()
            if row:
                columns = [
                    "user_id", "user_name", "screen_time", "focus", "changes",
                    "feedback", "after_screen_time", "after_focus", "is_useful",
                    "whats_new", "whats_changed", "else_challenge", "topics"
                ]
                return {columns[i]: row[i] for i in range(len(columns))}
            return None
    return await retry_async(_get)

async def delete_user(user_id: int):
    async def _delete():
        async with aiosqlite.connect("bot.db") as conn:
            await conn.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
            await conn.commit()
        logging.info(f"Пользователь {user_id} удалён из базы")
    await retry_async(_delete)

async def get_active_users() -> List[int]:
    async def _get_active():
        async with aiosqlite.connect("bot.db") as conn:
            cursor = await conn.execute("SELECT user_id FROM users")
            rows = await cursor.fetchall()
            return [user_id for (user_id,) in rows]
    return await retry_async(_get_active)

async def get_name(user_id: int) -> Optional[str]:
    async def _get_name():
        async with aiosqlite.connect("bot.db") as conn:
            cursor = await conn.execute("SELECT user_name FROM users WHERE user_id = ?", (user_id,))
            row = await cursor.fetchone()
            return row[0] if row else None
    return await retry_async(_get_name)

async def get_all_users_data() -> List[Dict[str, Any]]:
    async def _get_all():
        async with aiosqlite.connect("bot.db") as conn:
            cursor = await conn.execute("SELECT * FROM users")
            rows = await cursor.fetchall()
            columns = [
                "user_id", "user_name", "screen_time", "focus", "changes",
                "feedback", "after_screen_time", "after_focus", "is_useful",
                "whats_new", "whats_changed", "else_challenge", "topics"
            ]
            return [{columns[i]: row[i] for i in range(len(columns))} for row in rows]
    return await retry_async(_get_all)
