import aiosqlite
import logging
from typing import Optional, Dict, Any

import aiosqlite
import logging

async def init_db():
    async with aiosqlite.connect("bot.db") as conn:
        # Таблица пользователей
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

        # Таблица FSM (с дефолтным пустым JSON для data)
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS fsm_storage (
                key TEXT PRIMARY KEY,
                state TEXT,
                data TEXT DEFAULT '{}'
            );
        ''')

        await conn.commit()
    logging.info("База данных инициализирована")


async def save_user_data(user_id: int, **fields: Optional[str]) -> None:
    """
    Универсальная функция сохранения данных пользователя.
    Передаёшь user_id и любое количество полей: сохранит только их.
    Пример:
        await save_user_data(123, user_name="Иван", screen_time="2 часа")
    """
    if not fields:
        return

    async with aiosqlite.connect("bot.db") as conn:
        # Проверяем, есть ли уже запись о пользователе
        cursor = await conn.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
        exists = await cursor.fetchone()

        if exists:
            # Формируем UPDATE только по переданным полям
            update_fields = [f"{col} = ?" for col in fields.keys()]
            params = list(fields.values()) + [user_id]
            query = f"UPDATE users SET {', '.join(update_fields)} WHERE user_id = ?"
            await conn.execute(query, params)
        else:
            # INSERT с нужными колонками
            columns = ["user_id"] + list(fields.keys())
            placeholders = ["?"] * len(columns)
            params = [user_id] + list(fields.values())
            query = f"INSERT INTO users ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
            await conn.execute(query, params)

        await conn.commit()
    logging.info(f"Данные пользователя {user_id} обновлены: {fields}")

async def get_user_data(user_id: int) -> Optional[Dict[str, Any]]:
    async with aiosqlite.connect("bot.db") as conn:
        cursor = await conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        result = await cursor.fetchone()
        if result:
            return {
                "user_id": result[0],
                "user_name": result[1],
                "screen_time": result[2],
                "focus": result[3],
                "changes": result[4],
                "feedback": result[5],
                "after_screen_time": result[6],
                "after_focus": result[7],
                "is_useful": result[8],
                "whats_new": result[9],
                "whats_changed": result[10],
                "else_challenge": result[11],
                "topics": result[12],
            }
        return None

async def delete_user(user_id: int):
    async with aiosqlite.connect("bot.db") as conn:
        await conn.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        await conn.commit()
    logging.info(f"Пользователь {user_id} удалён из базы")

async def get_active_users():
    async with aiosqlite.connect("bot.db") as conn:
        cursor = await conn.execute("SELECT user_id FROM users")
        results = await cursor.fetchall()
        # Извлекаем только user_id из кортежей
        return [user_id for (user_id,) in results]

async def get_name(user_id: int) -> str | None:
    async with aiosqlite.connect("bot.db") as conn:
        cursor = await conn.execute(
            "SELECT user_name FROM users WHERE user_id = ?", (user_id,)
        )
        row = await cursor.fetchone()
        return row[0] if row else None