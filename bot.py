import asyncio
from os import getenv
import sys
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
import logging
from aiogram.client.default import DefaultBotProperties
from aiogram.exceptions import TelegramNetworkError
from aiohttp.client_exceptions import ClientConnectorError, ClientConnectorDNSError
from aiogram.client.session.aiohttp import AiohttpSession

from app.handlers.start_dialogue import router as start_router
from app.handlers.admin import admin_router
from app.handlers.final_dialogue import router as final_router
from app.scheduler import scheduler, restore_scheduled_jobs
from app.database import init_db
from app.utils.context import bot_var, dp_var
from app.utils.storage import SQLiteStorage

# Настройка логирования
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
#logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", filename="bot.log", encoding="utf-8")
logging.getLogger('apscheduler').setLevel(logging.DEBUG)


RETRY_EXC = (TelegramNetworkError, ClientConnectorError, ClientConnectorDNSError, asyncio.TimeoutError, OSError)

async def run_polling_forever(bot: Bot, dp: Dispatcher):
    backoff = 2
    while True:
        try:
            await dp.start_polling(bot)
            # если вышли без исключений — значит нас остановили корректно
            break
        except RETRY_EXC as e:
            logging.warning(f"Polling network error: {e}. Retry in {backoff}s")
            await asyncio.sleep(min(backoff, 30))
            backoff = min(backoff * 2, 30)
        except Exception:
            logging.exception("Fatal error in polling. Stopping.")
            break

async def main() -> None:
    """
    Основная функция для запуска бота.
    Инициализирует базу данных, восстанавливает задачи планировщика и запускает бота.
    """
    load_dotenv()
    session = AiohttpSession()
    bot = Bot(
        token=getenv("BOT_TOKEN"),
        session=session,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

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

    # Запуск планировщика
    if not scheduler.running:
        scheduler.configure(
            job_defaults={
                "coalesce": True,          # слить пропущенные срабатывания в одно
                "max_instances": 1,        # не плодить конкурентные отправки
                "misfire_grace_time": 300  # обработать триггер, если опоздали до 5 минут
            }
        )
        scheduler.start()
        logging.info("Планировщик запущен")

    # Восстановление запланированных задач
    await restore_scheduled_jobs(bot, dp)

    try:
        await run_polling_forever(bot, dp)
    finally:
        # Завершаем аккуратно только при реальном выходе
        await dp.storage.close()
        await bot.session.close()
        if scheduler.running:
            scheduler.shutdown()
        logging.info("Бот остановлен")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен.")

