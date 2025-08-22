import aiosqlite
import logging
from typing import Optional, Dict, Any

async def init_db():
    async with aiosqlite.connect("bot.db") as conn:
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                user_name TEXT,
                screen_time TEXT,
                focus TEXT,
                changes TEXT,
                selected_time TEXT,
                after_screen_time TEXT,
                after_focus TEXT,
                start_date TEXT,
                days_left INTEGER,
                is_useful TEXT,
                whats_new TEXT,
                whats_changed TEXT
            );
        ''')
        await conn.commit()
    logging.info("База данных инициализирована")

async def save_user_data(user_id: int,
                         days_left: int,
                         user_name: Optional[str] = None,
                         screen_time: Optional[str] = None,
                         focus: Optional[str] = None,
                         changes: Optional[str] = None,
                         selected_time: Optional[str] = None,
                         start_date: Optional[str] = None):
    async with aiosqlite.connect("bot.db") as conn:
        await conn.execute('''
            INSERT OR REPLACE INTO users 
            (user_id, user_name, screen_time, focus, changes, selected_time, start_date, days_left)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, user_name, screen_time, focus, changes, selected_time, start_date, days_left))
        await conn.commit()
    logging.info(f"Данные пользователя {user_id} сохранены")

async def save_final_answer(user_id: int,
                            after_screen_time: Optional[str] = None,
                            after_focus: Optional[str] = None,
                            is_useful: Optional[str] = None,
                            whats_new: Optional[str] = None,
                            whats_changed: Optional[str] = None):
    async with aiosqlite.connect("bot.db") as conn:
        # Обновляем только те поля, которые переданы (не None)
        update_fields = []
        params = []

        if after_screen_time is not None:
            update_fields.append("after_screen_time = ?")
            params.append(after_screen_time)
        if after_screen_time is not None:
            update_fields.append("after_focus = ?")
            params.append(after_focus)

        if is_useful is not None:
            update_fields.append("is_useful = ?")
            params.append(is_useful)
        if whats_new is not None:
            update_fields.append("whats_new = ?")
            params.append(whats_new)
        if whats_changed is not None:
            update_fields.append("whats_changed = ?")
            params.append(whats_changed)

        if update_fields:
            params.append(user_id)
            query = f"UPDATE users SET {', '.join(update_fields)} WHERE user_id = ?"
            await conn.execute(query, params)
            await conn.commit()
            logging.info(f"Дополнительные ответы пользователя {user_id} сохранены")

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
                "selected_time": result[5],
                "goal": result[6],
                "after_screen_time": result[7],
                "after_focus": result[8],
                "start_date": result[9],
                "days_left": result[10],
                "is_useful": result[11],
                "whats_new": result[12],
                "whats_changed": result[13]
            }
        return None

async def update_user_days_left(user_id: int, days_left: int):
    async with aiosqlite.connect("bot.db") as conn:
        await conn.execute("UPDATE users SET days_left = ? WHERE user_id = ?", (days_left, user_id))
        await conn.commit()

async def delete_user(user_id: int):
    async with aiosqlite.connect("bot.db") as conn:
        await conn.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        await conn.commit()
    logging.info(f"Пользователь {user_id} удалён из базы")

async def get_active_users():
    async with aiosqlite.connect("bot.db") as conn:
        cursor = await conn.execute("SELECT user_id, selected_time FROM users WHERE days_left > 0")
        return await cursor.fetchall()