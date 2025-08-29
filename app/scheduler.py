"""
Модуль для работы с планировщиком задач (apscheduler).
Обрабатывает отправку ежедневных уведомлений с аудио и восстановление задач при перезапуске.
"""
from datetime import datetime, timedelta
from os import getenv
from typing import Dict
from zoneinfo import ZoneInfo
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from aiogram import Bot
import logging
from aiogram.fsm.context import FSMContext
from app.database import get_user_data, get_active_users

from app.messages import START_DAY, CHANNEL_ID, timetable_single_messages, dialogue_messages, questions
from app.utils.audio import send_audio_challenge
from app.cash.cash import messages_meta
import app.keyboards as kb
from app.utils.form import UserForm

scheduler = AsyncIOScheduler()

async def run_final_questions(bot: Bot, user_id: int, state: FSMContext | None = None):
    try:
        await bot.forward_message(
            chat_id=user_id,
            from_chat_id=CHANNEL_ID,
            message_id=dialogue_messages.get('final_questions_start', {}).get('forward_key')
        )
        await bot.send_message(
            chat_id=user_id,
            text=questions.get('after_screen_time'),
            reply_markup=kb.get_screen_time_keyboard()
        )
        if state:
            await state.set_state(UserForm.waiting_for_after_screen_time)

        logging.info(f"Начат финальный опрос пользователя {user_id}")

    except Exception as e:
        logging.error(f"Ошибка при запуске финальных вопросов для пользователя {user_id}: {e}")

def get_number_day() -> int:
    """Возвращает количество дней после START_DAY (положительное число)"""
    start_date = datetime.strptime(START_DAY, "%Y-%m-%d").date()
    current_date = datetime.now().date()
    delta =  current_date - start_date
    return delta.days + 1

def get_next_day():
    """Возвращает количество дней после START_DAY (положительное число)"""
    for i in range(1, 16):
        yield i

g = get_next_day()

async def send_task(bot: Bot, user_id: int, day_num:int|None=None):
    if day_num:
        day = day_num
    else:
        day = g.__next__()
        #day = get_number_day()

    data = await get_user_data(user_id)

    # if not data:
    #     logging.error(f"{user_id} не зарегистрированы в марафоне, задания {day} дня не направлены ему")
    #     return
    #
    # if day < 1:
    #     logging.error(f"Марафон не начался для пользователя {user_id}")
    #     return
    #
    # if day > 16:
    #     logging.error(f"Марафон завершен для пользователя {user_id}")
    #     # удалить из списка задач
    #     return

    try:
        await send_audio_challenge(bot=bot, user_id=user_id, key=str(day))
        await bot.forward_message(
            chat_id=user_id,
            from_chat_id=CHANNEL_ID,
            message_id=int(messages_meta.get(str(day)).get("forward_key"))
        )

    except Exception as e:
        logging.error(f"Ошибка отправки задания {day} дня пользователю {user_id}: {str(e)}")


async def schedule_tasks(bot: Bot, user_id: int, selected_time: str, start_date: str):
    minute, hour,  = 0, int(selected_time.split("_")[1])
    end_date = datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=14)
    scheduler.add_job(
        send_task,
        trigger=CronTrigger(
            hour=hour,
            minute=minute,
            start_date=start_date,
            end_date=end_date,
            #minute='*', # Каждую минуту,
            timezone=ZoneInfo("Europe/Moscow")
        ),
        args=[bot, user_id],
        max_instances=1,
        replace_existing=True,
        id=f"task_{user_id}"  # Уникальный ID для задачи
    )
    logging.info(f"Направление регулярных заданий запланированы для пользователя {user_id} на {selected_time}")

async def send_single_message(bot: Bot, user_id: int, date_time:Dict):
    message_key = date_time.get("message_key")
    audio = date_time.get("audio")
    forward_key = date_time.get('forward_key')
    if audio:
        await send_audio_challenge(bot, user_id, message_key)
    try:
        await bot.forward_message(
            chat_id=user_id,
            from_chat_id=CHANNEL_ID,
            message_id=forward_key
        )
    except Exception as e:
        logging.error(f"Ошибка отправки уведомления {message_key} пользователю {user_id}: {e}")


async def schedule_single_messages(bot: Bot, user_id: int):
    for date_time in timetable_single_messages:
        # добавить сравнение с текущей датой, добавление последующих
        message_key = date_time.get("message_key")
        time = date_time.get("time") if date_time.get("time") else {}
        if time:
            if message_key == "final":
                scheduler.add_job(
                    run_final_questions,
                    trigger=CronTrigger(
                        **time,
                        timezone=ZoneInfo("Europe/Moscow")
                    ),
                    args=[bot, user_id],
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
            # scheduler.add_job(
            #     send_single_message,
            #     trigger=CronTrigger(
            #         **time,
            #         timezone=ZoneInfo("Europe/Moscow")
            #     ),
            #     args=[bot, user_id, date_time],
            #     max_instances=1,
            #     replace_existing=True,
            #     id=f"{message_key}_{user_id}"  # Уникальный ID для задачи
            # )
            logging.info(f"Уведомление {message_key} запланировано для пользователя {user_id} на {time}")

async def restore_scheduled_jobs(bot: Bot):
    """
    Восстанавливает запланированные задачи из базы данных при перезапуске бота.

    Args:
        bot: Экземпляр бота для отправки сообщений.
    """
    active_users = await get_active_users()
    for user_id, selected_time in active_users:
        await schedule_tasks(bot, user_id, selected_time, start_date=START_DAY)
        await schedule_single_messages(bot, user_id)
        pass

    logging.info(f"Восстановлено {len(active_users)} задач из базы данных")


# рассылка без блокировки
# добавление рассылки по графику
# проверка нормальной работы с бд
# ревью ии-шками
# тесты
# выбор места размещения
# размещение