"""
Модуль для работы с базой данных SQLite через aiosqlite.
Содержит функции для инициализации базы, сохранения данных и управления уведомлениями.
"""

import aiosqlite
import logging

async def init_db():
    """
    Инициализирует базу данных, создавая таблицу users, если она не существует.
    Таблица содержит Telegram ID пользователя, выбранное время, ответы на вопросы,
    дату начала и количество оставшихся дней.
    """
    async with aiosqlite.connect("bot.db") as conn:
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                selected_time TEXT,
                answer1 TEXT,
                answer2 TEXT,
                answer3 TEXT,
                answer4 TEXT,
                start_date TEXT,
                days_left INTEGER
            )
        ''')
        await conn.commit()
    logging.info("База данных инициализирована")

async def save_user_data(user_id: int, selected_time: str, answer1: str, answer2: str,
                         answer3: str, answer4: str, start_date: str, days_left: int):
    """
    Сохраняет данные пользователя в базу.

    Args:
        user_id: Telegram ID пользователя.
        selected_time: Выбранное время для уведомлений (например, "08:00").
        answer1, answer2, answer3, answer4: Ответы пользователя на вопросы.
        start_date: Дата начала марафона (строка в формате YYYY-MM-DD).
        days_left: Количество оставшихся дней (15 для нового марафона).
    """
    async with aiosqlite.connect("bot.db") as conn:
        await conn.execute('''
            INSERT OR REPLACE INTO users (user_id, selected_time, answer1, answer2, answer3, answer4, start_date, days_left)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, selected_time, answer1, answer2, answer3, answer4, start_date, days_left))
        await conn.commit()
    logging.info(f"Данные пользователя {user_id} сохранены")

async def get_user_data(user_id: int) -> tuple:
    """
    Получает данные пользователя из базы.

    Args:
        user_id: Telegram ID пользователя.

    Returns:
        Кортеж с данными (days_left) или None, если пользователь не найден.
    """
    async with aiosqlite.connect("bot.db") as conn:
        cursor = await conn.execute("SELECT days_left FROM users WHERE user_id = ?", (user_id,))
        return await cursor.fetchone()

async def update_user_days_left(user_id: int, days_left: int):
    """
    Обновляет количество оставшихся дней для пользователя.

    Args:
        user_id: Telegram ID пользователя.
        days_left: Новое количество оставшихся дней.
    """
    async with aiosqlite.connect("bot.db") as conn:
        await conn.execute("UPDATE users SET days_left = ? WHERE user_id = ?", (days_left, user_id))
        await conn.commit()

async def delete_user(user_id: int):
    """
    Удаляет пользователя из базы.

    Args:
        user_id: Telegram ID пользователя.
    """
    async with aiosqlite.connect("bot.db") as conn:
        await conn.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        await conn.commit()
    logging.info(f"Пользователь {user_id} удалён из базы")

async def get_active_users():
    """
    Получает список активных пользователей для восстановления задач.

    Returns:
        Список кортежей (user_id, selected_time) для пользователей с days_left > 0.
    """
    async with aiosqlite.connect("bot.db") as conn:
        cursor = await conn.execute("SELECT user_id, selected_time FROM users WHERE days_left > 0")
        return await cursor.fetchall()