import asyncio
from os import getenv
import os
import json
import sys
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.base import BaseStorage, StateType
import aiosqlite

from app.cash.cash import load_cache
from app.handlers.start_dialogue import router as start_router
from app.handlers.admin import admin_router
from app.handlers.final_dialogue import router as final_router
from app.scheduler import scheduler, restore_scheduled_jobs
from app.database import init_db
from app.utils.context import bot_var, dp_var

# Настройка логирования
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
#logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", filename="bot.log", encoding="utf-8")
logging.getLogger('apscheduler').setLevel(logging.DEBUG)

import aiosqlite
import json
import logging
from typing import Any, Dict, Optional
from aiogram.fsm.storage.base import BaseStorage, StorageKey, StateType


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
        key_str = self._key_to_string(key)
        state_str = self._state_to_string(state)
        async with aiosqlite.connect(self.db_path) as conn:
            # сохраняем state, но не затираем data
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

    async def get_state(self, key: StorageKey) -> Optional[str]:
        key_str = self._key_to_string(key)
        async with aiosqlite.connect(self.db_path) as conn:
            cursor = await conn.execute("SELECT state FROM fsm_storage WHERE key=?", (key_str,))
            row = await cursor.fetchone()
            return row[0] if row else None

    async def set_data(self, key: StorageKey, data: Dict[str, Any]) -> None:
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

    async def get_data(self, key: StorageKey) -> Dict[str, Any]:
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

    async def delete_state(self, key: StorageKey) -> None:
        key_str = self._key_to_string(key)
        async with aiosqlite.connect(self.db_path) as conn:
            await conn.execute("DELETE FROM fsm_storage WHERE key=?", (key_str,))
            await conn.commit()
        logging.debug(f"State deleted for {key_str}")

    async def close(self) -> None:
        pass


async def main() -> None:
    """
    Основная функция для запуска бота.
    Инициализирует базу данных, восстанавливает задачи планировщика и запускает бота.
    """
    load_dotenv()
    bot = Bot(
        token=getenv("BOT_TOKEN"),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    # --- Загрузка кеша аудио ---
    load_cache()

    # Инициализация SQLiteStorage
    storage = SQLiteStorage(db_path="bot.db")
    dp = Dispatcher(storage=storage)
    dp.include_router(start_router)
    dp.include_router(final_router)
    dp.include_router(admin_router)

    # сохраняем в контекст
    bot_var.set(bot)
    dp_var.set(dp)

    # Инициализация базы данных
    await init_db()

    # Восстановление запланированных задач
    await restore_scheduled_jobs(bot, dp)

    # Запуск планировщика
    scheduler.start()
    logging.info("Планировщик запущен")

    try:
        await dp.start_polling(bot)
    finally:
        await dp.storage.close()
        await bot.session.close()
        scheduler.shutdown()
        logging.info("Бот остановлен")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен.")


# """
# Основной файл для запуска Telegram-бота.
# Инициализирует бота, базу данных и планировщик, а также запускает обработку сообщений.
# """
# import asyncio
# from os import getenv
# import os
# import json
# import sys
# import logging
# from dotenv import load_dotenv
#
# from aiogram import Bot, Dispatcher
# from aiogram.client.default import DefaultBotProperties
# from aiogram.enums import ParseMode
#
# from app.cash.cash import load_cache
# from app.handlers.start_dialogue import router as start_router
# from app.handlers.admin import admin_router
# from app.handlers.final_dialogue import router as final_router
# from app.scheduler import scheduler, restore_scheduled_jobs
# from app.database import init_db
#
# # Настройка логирования
# logging.basicConfig(level=logging.INFO, stream=sys.stdout)
# logging.getLogger('apscheduler').setLevel(logging.DEBUG)
# #logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", filename="bot.log", encoding="utf-8")
#
#
# async def main() -> None:
#     """
#     Основная функция для запуска бота.
#     Инициализирует базу данных, восстанавливает задачи планировщика и запускает бота.
#     """
#
#     load_dotenv()
#     bot = Bot(
#         token=getenv("BOT_TOKEN"),
#         default=DefaultBotProperties(parse_mode=ParseMode.HTML)
#     )
#
#     # --- Загрузка кеша аудио ---
#     load_cache()
#
#     dp = Dispatcher()
#     dp.include_router(start_router)
#     dp.include_router(final_router)
#     dp.include_router(admin_router)
#
#     # Инициализация базы данных
#     await init_db()
#
#     # Восстановление запланированных задач
#     await restore_scheduled_jobs(bot, dp)
#
#     # Запуск планировщика
#     scheduler.start()
#     logging.info("Планировщик запущен")
#
#     try:
#         await dp.start_polling(bot)
#     finally:
#         await dp.storage.close()
#         await bot.session.close()
#         scheduler.shutdown()
#         logging.info("Бот остановлен")
#
# if __name__ == "__main__":
#     try:
#         asyncio.run(main())
#     except KeyboardInterrupt:
#         print("Бот выключен.")
