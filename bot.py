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

from app.handlers.main_dialogue import router as main_router
from app.handlers.test_dialogue import router as test_router
from app.handlers.questions import router as questions_router
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
    dp = Dispatcher()
    dp.include_router(main_router)
    dp.include_router(test_router)
    dp.include_router(questions_router)

    # Инициализация базы данных
    await init_db()

    # Восстановление запланированных задач
    await restore_scheduled_jobs(bot)

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
