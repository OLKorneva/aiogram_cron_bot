"""
Основной файл для запуска Telegram-бота.
Инициализирует бота, базу данных и планировщик, а также запускает обработку сообщений.
"""
import asyncio
from os import getenv
import os
import json
import sys
import logging
from dotenv import load_dotenv
from aiogram.fsm.storage.sqlalchemy import SQLAlchemyStorage, Base

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.cash.cash import load_cache
from app.handlers.start_dialogue import router as start_router
from app.handlers.admin import admin_router
from app.handlers.final_dialogue import router as final_router
from app.scheduler import scheduler, restore_scheduled_jobs
from app.database import init_db

# Настройка логирования
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logging.getLogger('apscheduler').setLevel(logging.DEBUG)
#logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", filename="bot.log", encoding="utf-8")


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
    BOT_TOKEN = getenv("BOT_TOKEN")
    DB_URL = getenv("DB_URL")


    dp = Dispatcher()
    dp.include_router(start_router)
    dp.include_router(final_router)
    dp.include_router(admin_router)

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


"""
Основной файл для запуска Telegram-бота.
Инициализирует бота, базу данных и планировщик, а также запускает обработку сообщений.
"""
import asyncio
from os import getenv
import sys
import logging
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode


from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.cash.cash import load_cache
from app.handlers.start_dialogue import router as start_router
from app.handlers.admin import admin_router
from app.handlers.final_dialogue import router as final_router
from app.scheduler import scheduler, restore_scheduled_jobs
from app.database import init_db

# Настройка логирования
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logging.getLogger('apscheduler').setLevel(logging.DEBUG)


async def main() -> None:
    """
    Основная функция для запуска бота.
    Инициализирует базу данных, FSM, восстанавливает задачи планировщика и запускает бота.
    """

    load_dotenv()
    BOT_TOKEN = getenv("BOT_TOKEN")
    DB_URL = getenv("DB_URL")  # sqlite+aiosqlite:///db.sqlite3

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    # --- FSM через SQLite ---
    engine = create_async_engine(DB_URL, echo=False, future=True)
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
    storage = SQLAlchemyStorage(sessionmaker, Base)

    # Создаём таблицы FSM (один раз при старте)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # --- Dispatcher ---
    dp = Dispatcher(storage=storage)
    dp.include_router(start_router)
    dp.include_router(final_router)
    dp.include_router(admin_router)

    # --- Загрузка кеша аудио ---
    load_cache()

    # --- Инициализация базы данных проекта (твоя app.database.init_db) ---
    await init_db()

    # --- Восстановление запланированных задач ---
    await restore_scheduled_jobs(bot, dp)

    # --- Запуск планировщика ---
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
