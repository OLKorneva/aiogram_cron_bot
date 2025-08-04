"""
Модуль для работы с планировщиком задач (apscheduler).
Обрабатывает отправку ежедневных уведомлений с аудио и восстановление задач при перезапуске.
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from aiogram import Bot
import logging
import os
from app.database import get_user_data, update_user_days_left, delete_user, get_active_users
from app.messages import MESSAGES

scheduler = AsyncIOScheduler()

async def send_notification(bot: Bot, user_id: int):
    """
    Отправляет уведомление пользователю с аудиофайлом для текущего дня.
    Обновляет количество оставшихся дней и удаляет пользователя после последнего дня.

    Args:
        bot: Экземпляр бота для отправки сообщений.
        user_id: Telegram ID пользователя, используется как chat_id для личных сообщений.
    """
    user_data = await get_user_data(user_id)
    if user_data:
        days_left = user_data.get("days_left", None)
        if days_left is not None and days_left > 0:
            day = 17 - days_left  # Номер текущего дня (1–15)
            audio_path = os.path.join("app", "audio", f"day{day}.mp3")
            try:
                if not os.path.exists(audio_path):
                    logging.error(f"Аудиофайл {audio_path} не найден")
                    await bot.send_message(user_id, MESSAGES.get(day, ''))  # Отправляем только текст
                    return
                with open(audio_path, "rb") as audio_file:
                    await bot.send_audio(user_id, audio=audio_file, caption=MESSAGES.get(day, ''))
                await update_user_days_left(user_id, days_left - 1)
                logging.info(f"Уведомление отправлено пользователю {user_id}, день {day}, осталось дней: {days_left - 1}")
                if days_left == 1:  # После последнего уведомления
                    await delete_user(user_id)
                    logging.info(f"Уведомления для пользователя {user_id} завершены")
            except Exception as e:
                logging.error(f"Ошибка отправки уведомления пользователю {user_id}: {e}")
                await delete_user(user_id)  # Удаляем, если пользователь недоступен

async def schedule_notification(bot: Bot, user_id: int, selected_time: str):
    """
    Планирует ежедневные уведомления для пользователя.

    Args:
        bot: Экземпляр бота для отправки сообщений.
        user_id: Telegram ID пользователя, используется как chat_id.
        selected_time: Выбранное время для уведомлений (например, "08:00").
    """
    hour, minute = map(int, selected_time.split(":"))
    scheduler.add_job(
        send_notification,
        trigger=CronTrigger(hour=hour, minute=minute),
        args=[bot, user_id],
        max_instances=1,
        replace_existing=True,
        id=f"notification_{user_id}"  # Уникальный ID для задачи
    )
    logging.info(f"Уведомления запланированы для пользователя {user_id} на {selected_time}")

async def restore_scheduled_jobs(bot: Bot):
    """
    Восстанавливает запланированные задачи из базы данных при перезапуске бота.

    Args:
        bot: Экземпляр бота для отправки сообщений.
    """
    active_users = await get_active_users()
    for user_id, selected_time in active_users:
        await schedule_notification(bot, user_id, selected_time)
    logging.info(f"Восстановлено {len(active_users)} задач из базы данных")