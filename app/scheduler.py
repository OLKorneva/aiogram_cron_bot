from typing import Dict
from zoneinfo import ZoneInfo
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from aiogram import Bot
import logging
from aiogram.fsm.context import FSMContext
from app.database import get_active_users, get_name

from app.messages import CHANNEL_ID, timetable_single_messages, dialogue_messages, questions
import app.keyboards as kb
from app.utils.form import UserForm

scheduler = AsyncIOScheduler()

async def send_single_message(bot: Bot, user_id: int, date_time:Dict):
    message_key = date_time.get("message_key")
    forward_key = date_time.get('forward_key')
    try:
        if forward_key:
            await bot.forward_message(
                chat_id=user_id,
                from_chat_id=CHANNEL_ID,
                message_id=forward_key
            )
            logging.info(f"Сообщение {message_key} отправлено пользователю {user_id}")
        else:
            logging.error(f"forward_key в {date_time} не найден, это сообщение пользователю {user_id} не направлено")
    except Exception as e:
        logging.error(f"Ошибка отправки сообщения {message_key} пользователю {user_id}: {e}")

from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey


async def run_final_questions(bot: Bot, user_id: int, dp):
    try:
        # достаём FSMContext для конкретного пользователя
        state = FSMContext(
            storage=dp.storage,
            key=StorageKey(bot_id=bot.id, chat_id=user_id, user_id=user_id)
        )

        # имя пользователя
        name = await get_name(user_id)

        # первое сообщение
        await bot.send_message(
            chat_id=user_id,
            text=questions.get('final_questions').format(name or '')
        )

        # первый вопрос с клавиатурой
        await bot.send_message(
            chat_id=user_id,
            text=questions.get('after_screen_time'),
            reply_markup=kb.get_screen_time_keyboard()
        )

        # ставим состояние
        await state.set_state(UserForm.waiting_for_after_screen_time)

        logging.info(f"Начат финальный опрос пользователя {user_id}")

    except Exception as e:
        logging.error(f"Ошибка при запуске финальных вопросов для пользователя {user_id}: {e}")


async def run_middle_question(bot: Bot, user_id: int, dp):
    try:
        state = FSMContext(
            storage=dp.storage,
            key=StorageKey(bot_id=bot.id, chat_id=user_id, user_id=user_id)
        )

        name = await get_name(user_id)
        await bot.send_message(
            chat_id=user_id,
            text=questions.get('feedback').format(name or ''),
            reply_markup=kb.get_feedback()
        )

        await state.set_state(UserForm.waiting_for_feedback)

        logging.info(f"Запрошен отзыв у пользователя {user_id}")

    except Exception as e:
        logging.error(f'Ошибка запроса отзыва у пользователя {user_id}: {e}')



async def schedule_single_messages(bot: Bot, user_id: int, dp):
    for date_time in timetable_single_messages:
        message_key = date_time.get("message_key")
        time = date_time.get("time")
        if time:
            if message_key == "final":
                scheduler.add_job(
                    run_final_questions,
                    trigger=CronTrigger(
                        **time,
                        timezone=ZoneInfo("Europe/Moscow")
                    ),
                    args=[bot, user_id, dp],
                    max_instances=1,
                    replace_existing=True,
                    id=f"{message_key}_{user_id}"
                )
            elif message_key == "feedback":
                scheduler.add_job(
                    run_middle_question,
                    trigger=CronTrigger(
                        **time,
                        timezone=ZoneInfo("Europe/Moscow")
                    ),
                    args=[bot, user_id, dp],
                    max_instances=1,
                    replace_existing=True,
                    id=f"{message_key}_{user_id}"
                )
            else:
                scheduler.add_job(
                    send_single_message,
                    trigger=CronTrigger(
                        **time,
                        timezone=ZoneInfo("Europe/Moscow")
                    ),
                    args=[bot, user_id, date_time],
                    max_instances=1,
                    replace_existing=True,
                    id=f"{message_key}_{user_id}"
                )
            logging.info(f"Уведомление {message_key} запланировано для пользователя {user_id} на {time}")

async def restore_scheduled_jobs(bot: Bot, dp):
    active_users = await get_active_users()
    for user_id in active_users:
        await schedule_single_messages(bot, user_id, dp)
    logging.info(f"Восстановлено {len(active_users)} задач из базы данных")


# рассылка без блокировки
# добавление рассылки по графику
# проверка нормальной работы с бд: ин мемори? как нормально? почему при перезапуске и начале опроса предыдущие данные о финальных ответах потерялис?
#запретить повторный ввод по нажатию старт
# сделать сохранение в бд ответов из состояния при ошибке в середине
# ревью ии-шками
# тесты
# сделать чтобы не падала, если стартовых ответов нет, а задаются финальные
# выбор места размещения
# размещение