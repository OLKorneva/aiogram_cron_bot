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
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError, TelegramRetryAfter

from app.database import get_active_users, get_name
from app.messages import CHANNEL_ID, timetable_single_messages, questions
import app.keyboards as kb
from app.utils.form import UserForm
from app.utils.retry import retry_async

# --- Настройка scheduler и semaphore ---
scheduler = AsyncIOScheduler()
MAX_CONCURRENT_SENDS = 4  # ограничение параллельных сообщений
semaphore = asyncio.Semaphore(MAX_CONCURRENT_SENDS)

# --- Безопасная отправка сообщения ---
async def send_single_message_safe(bot: Bot, user_id: int, date_time: Dict):
    async with semaphore:
        await asyncio.sleep(random.uniform(1.5, 2.5))  # небольшой рандом
        message_key = date_time.get("message_key")
        forward_key = date_time.get("forward_key")

        try:
            if forward_key:

                async def forward_single_message():
                    await bot.forward_message(
                        chat_id=user_id,
                        from_chat_id=CHANNEL_ID,
                        message_id=forward_key
                    )
                # Ретрай пересылки сообщения
                await retry_async(forward_single_message)

                logging.info(f"Сообщение {message_key} отправлено пользователю {user_id}")
            else:
                logging.error(f"forward_key в {date_time} не найден, сообщение не отправлено пользователю {user_id}")
        except TelegramForbiddenError as e:
            logging.warning(f"⚠️ Доступ запрещён для {user_id}: {e.message}")
        except TelegramBadRequest as e:
            logging.warning(f"⚠️ Неверный запрос для {user_id}: {e.message}")
        except TelegramRetryAfter as e:
            logging.error(f"⏳ Flood control: надо подождать {e.retry_after} сек")
            await asyncio.sleep(e.retry_after + 0.5)
            return await send_single_message_safe(bot, user_id, date_time)  # повторяем
        except Exception as e:
            logging.error(f"Ошибка отправки сообщения {message_key} пользователю {user_id}: {e}")
        finally:
            await asyncio.sleep(random.uniform(1.5, 2.5))  # небольшой рандом

# --- FSM-запросы ---

async def safe_send_message(bot: Bot, chat_id: int, **kwargs):
    async def _send():
        return await bot.send_message(chat_id=chat_id, **kwargs)
    return await retry_async(_send)


async def run_final_questions(bot: Bot, user_id: int, dp):
    async with semaphore:
        await asyncio.sleep(random.uniform(1.5, 2.5))  # небольшой рандом
        try:
            state = FSMContext(
                storage=dp.storage,
                key=StorageKey(bot_id=bot.id, chat_id=user_id, user_id=user_id)
            )
            name = await get_name(user_id)

            await safe_send_message(
                bot,
                user_id,
                text=questions['final_questions'].format(name or '')
            )
            await asyncio.sleep(random.uniform(1.0, 2.0))
            await safe_send_message(
                bot,
                user_id,
                text=questions['after_screen_time'],
                reply_markup=kb.get_screen_time_keyboard()
            )

            await state.set_state(UserForm.waiting_for_after_screen_time)
            logging.info(f"Начат финальный опрос пользователя {user_id}")
        except TelegramForbiddenError as e:
            logging.warning(f"⚠️ Доступ запрещён для {user_id}: {e.message}")
        except TelegramBadRequest as e:
            logging.warning(f"⚠️ Неверный запрос для {user_id}: {e.message}")
        except TelegramRetryAfter as e:
            logging.error(f"⏳ Flood control: надо подождать {e.retry_after} сек")
            await asyncio.sleep(e.retry_after + 0.5)
            return await run_final_questions(bot, user_id, dp)  # повторяем
        except Exception as e:
            logging.error(f"Ошибка при запуске финальных вопросов для пользователя {user_id}: {e}")
        finally:
            await asyncio.sleep(random.uniform(1.5, 2.5))  # небольшой рандом

async def run_middle_question(bot: Bot, user_id: int, dp):
    async with semaphore:
        await asyncio.sleep(random.uniform(1.5, 2.5))  # небольшой рандом
        try:
            state = FSMContext(
                storage=dp.storage,
                key=StorageKey(bot_id=bot.id, chat_id=user_id, user_id=user_id)
            )
            name = await get_name(user_id)

            await safe_send_message(
                bot,
                user_id,
                text=questions['feedback'].format(name or ''),
                reply_markup=kb.get_feedback()
            )
            await asyncio.sleep(random.uniform(1.5, 2.5))  # небольшой рандом
            await state.set_state(UserForm.waiting_for_feedback)
            logging.info(f"Запрошен отзыв у пользователя {user_id}")
        except TelegramForbiddenError as e:
            logging.warning(f"⚠️ Доступ запрещён для {user_id}: {e.message}")
        except TelegramBadRequest as e:
            logging.warning(f"⚠️ Неверный запрос для {user_id}: {e.message}")
        except TelegramRetryAfter as e:
            logging.error(f"⏳ Flood control: надо подождать {e.retry_after} сек")
            await asyncio.sleep(e.retry_after)
            return await run_middle_question(bot, user_id, dp)  # повторяем
        except Exception as e:
            logging.error(f"Ошибка запроса отзыва у пользователя {user_id}: {e}")
        finally:
            await asyncio.sleep(random.uniform(1.5, 2.5))  # небольшой рандом

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
