import asyncio
import logging
import random
from typing import Dict, List
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey

from app.database import get_active_users, get_name
from app.messages import CHANNEL_ID, timetable_single_messages, questions
import app.keyboards as kb
from app.utils.form import UserForm

# --- Настройка scheduler и semaphore ---
scheduler = AsyncIOScheduler()
MAX_CONCURRENT_SENDS = 10  # ограничение параллельных сообщений
semaphore = asyncio.Semaphore(MAX_CONCURRENT_SENDS)
BATCH_DELAY = 1  # секунда между батчами

# --- Безопасная отправка сообщения ---
async def send_single_message_safe(bot: Bot, user_id: int, date_time: Dict):
    async with semaphore:
        await asyncio.sleep(random.uniform(0.2, 0.5))  # небольшой рандом
        message_key = date_time.get("message_key")
        forward_key = date_time.get("forward_key")
        try:
            if forward_key:
                await bot.forward_message(
                    chat_id=user_id,
                    from_chat_id=CHANNEL_ID,
                    message_id=forward_key
                )
                logging.info(f"Сообщение {message_key} отправлено пользователю {user_id}")
            else:
                logging.error(f"forward_key в {date_time} не найден, сообщение не отправлено пользователю {user_id}")
        except Exception as e:
            logging.error(f"Ошибка отправки сообщения {message_key} пользователю {user_id}: {e}")

# --- FSM-запросы ---
async def run_final_questions(bot: Bot, user_id: int, dp):
    async with semaphore:
        await asyncio.sleep(random.uniform(0.2, 0.5))
        try:
            state = FSMContext(
                storage=dp.storage,
                key=StorageKey(bot_id=bot.id, chat_id=user_id, user_id=user_id)
            )
            name = await get_name(user_id)
            await bot.send_message(chat_id=user_id, text=questions.get('final_questions').format(name or ''))
            await bot.send_message(chat_id=user_id, text=questions.get('after_screen_time'), reply_markup=kb.get_screen_time_keyboard())
            await state.set_state(UserForm.waiting_for_after_screen_time)
            logging.info(f"Начат финальный опрос пользователя {user_id}")
        except Exception as e:
            logging.error(f"Ошибка при запуске финальных вопросов для пользователя {user_id}: {e}")

async def run_middle_question(bot: Bot, user_id: int, dp):
    async with semaphore:
        await asyncio.sleep(random.uniform(0.2, 0.5))
        try:
            state = FSMContext(
                storage=dp.storage,
                key=StorageKey(bot_id=bot.id, chat_id=user_id, user_id=user_id)
            )
            name = await get_name(user_id)
            await bot.send_message(chat_id=user_id, text=questions.get('feedback').format(name or ''), reply_markup=kb.get_feedback())
            await state.set_state(UserForm.waiting_for_feedback)
            logging.info(f"Запрошен отзыв у пользователя {user_id}")
        except Exception as e:
            logging.error(f"Ошибка запроса отзыва у пользователя {user_id}: {e}")

# --- Планирование задач для одного пользователя ---
async def schedule_single_messages(bot: Bot, user_id: int, dp):
    for date_time in timetable_single_messages:
        message_key = date_time.get("message_key")
        time = date_time.get("time")
        if not time:
            continue

        job_id = f"{message_key}_{user_id}"

        if message_key == "final":
            scheduler.add_job(
                run_final_questions,
                trigger=CronTrigger(**time, timezone=ZoneInfo("Europe/Moscow")),
                args=[bot, user_id, dp],
                max_instances=1,
                replace_existing=True,
                id=job_id
            )
        elif message_key == "feedback":
            scheduler.add_job(
                run_middle_question,
                trigger=CronTrigger(**time, timezone=ZoneInfo("Europe/Moscow")),
                args=[bot, user_id, dp],
                max_instances=1,
                replace_existing=True,
                id=job_id
            )
        else:
            scheduler.add_job(
                send_single_message_safe,
                trigger=CronTrigger(**time, timezone=ZoneInfo("Europe/Moscow")),
                args=[bot, user_id, date_time],
                max_instances=1,
                replace_existing=True,
                id=job_id
            )
        logging.info(f"Уведомление {message_key} запланировано для пользователя {user_id} на {time}")

# --- Восстановление рассылки для всех активных пользователей ---
async def restore_scheduled_jobs(bot: Bot, dp):
    active_users = await get_active_users()
    logging.info(f"Восстановление рассылки для {len(active_users)} пользователей")
    for user_id in active_users:
        await schedule_single_messages(bot, user_id, dp)

# --- Добавление нового пользователя в рассылку ---
async def add_new_user_to_schedule(bot: Bot, user_id: int, dp):
    await schedule_single_messages(bot, user_id, dp)
    logging.info(f"Новый пользователь {user_id} добавлен в рассылку")


# проверка нормальной работы с бд: ин мемори? как нормально? почему при перезапуске и начале опроса предыдущие данные о финальных ответах потерялис?
#запретить повторный ввод по нажатию старт
# ревью ии-шками
# тесты
# сделать чтобы не падала, если стартовых ответов нет, а задаются финальные
# выбор места размещения
# размещение