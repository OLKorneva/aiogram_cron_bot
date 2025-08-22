# """
# Модуль для работы с планировщиком задач (apscheduler).
# Обрабатывает отправку ежедневных уведомлений с аудио и восстановление задач при перезапуске.
# """
# from datetime import datetime
# from typing import Dict
# from zoneinfo import ZoneInfo
#
# from apscheduler.schedulers.asyncio import AsyncIOScheduler
# from aiogram.fsm.storage.base import StorageKey
# from aiogram.fsm.storage.memory import MemoryStorage
# from aiogram.fsm.context import FSMContext
# from apscheduler.triggers.cron import CronTrigger
# from aiogram.types import FSInputFile
# from aiogram import Bot
# import logging
# import os
# from app.database import get_user_data, get_active_users
# from app.handlers.questions import final_questions
# from app.messages import MESSAGES, timetable_single_messages, URL_MEETING_1
# from app.utils import format_text_to_width
#
# scheduler = AsyncIOScheduler()
#
# START_DAY = "2025-09-06"  # Ваша начальная дата в формате YYYY-MM-DD
#
#
# def get_number_day() -> int:
#     """Возвращает количество дней после START_DAY (положительное число)"""
#     start_date = datetime.strptime(START_DAY, "%Y-%m-%d").date()
#     current_date = datetime.now().date()
#     delta =  current_date - start_date
#     return delta.days + 1
#
# async def send_task(bot: Bot, user_id: int, day_num:int|None=None):
#     if not day_num:
#         day = i = get_number_day()
#     else:
#         day = i = day_num
#     data = await get_user_data(user_id)
#
#     if not data:
#         logging.error(f"{user_id} не зарегистрированы в марафоне, задания {day} дня не направлены ему")
#         return
#
#     if day < 1:
#         logging.error(f"Марафон не начался для пользователя {user_id}")
#         return
#
#     if day > 16:
#         logging.error(f"Марафон завершен для пользователя {user_id}")
#         # удалить из списка задач
#         return
#
#     user_name = data.get("user_name")
#     selected_time = data.get("selected_time")
#
#     try:
#         # Подготовка путей
#         image_path = os.path.join("app", "images", f"{i}.jpg")
#         audio_path = os.path.join("app", "audio", f"{i}.mp3")
#
#         # Получаем текст
#         text = MESSAGES.get(i)
#         if not text:
#             logging.error(f"Сообщение {i} дня не найдено")
#             return
#
#         # Всегда отправляем аудио первым
#         if os.path.exists(audio_path):
#             await bot.send_audio(
#                 chat_id=user_id,
#                 audio=FSInputFile(audio_path),
#                 title=f"День {i}",
#                 performer="Челлендж"
#             )
#
#         # Форматируем текст
#         if i == 1:
#             formated_text = text.format(user_name, URL_MEETING_1)
#         elif i == 2:
#             formated_text = text.format(user_name, selected_time)
#         else:
#             formated_text = text.format(user_name)
#
#         # Проверяем длину текста
#         if len(formated_text) <= 1024:
#             # Если текст короткий - отправляем видео с текстом в подписи
#
#             if os.path.exists(image_path):
#                 await bot.send_photo(user_id, FSInputFile(image_path), caption=formated_text)
#
#         else:
#             # Если текст длинный - отправляем все по отдельности
#             if os.path.exists(image_path):
#                 await bot.send_photo(
#                     chat_id=user_id,
#                     photo=FSInputFile(image_path)
#                 )
#             # Форматируем текст
#             format_text = format_text_to_width(formated_text, 680)
#             await bot.send_message(user_id, format_text)
#
#         logging.info(f"Задания дня {i} дня отправлены {user_id}")
#
#         if i == 16:  # После последнего уведомления
#             logging.info(f"Уведомления для пользователя {user_id} завершены")
#     except Exception as e:
#         logging.error(f"Ошибка отправки задания {i} дня пользователю {user_id}: {str(e)}")
#
#
# async def schedule_tasks(bot: Bot, user_id: int, selected_time: str, start_date: str|datetime):
#     hour, minute = map(int, selected_time.split(":"))
#     scheduler.add_job(
#         send_task,
#         trigger=CronTrigger(
#             hour=hour,
#             minute=minute,
#             start_date=start_date,
#             #second=48,
#             timezone=ZoneInfo("Europe/Moscow")
#         ),
#         args=[bot, user_id],
#         max_instances=1,
#         replace_existing=True,
#         id=f"task_{user_id}"  # Уникальный ID для задачи
#     )
#     logging.info(f"Направление регулярных заданий запланированы для пользователя {user_id} на {selected_time}")
#
#
# async def send_single_message(bot: Bot, user_id: int, date_time:Dict):
#     user_data = await get_user_data(user_id)
#     message_key = date_time.get("message_key")
#     if user_data:
#         user_name = user_data.get("user_name")
#         audio = date_time.get("audio")
#         image = date_time.get("image")
#         url = date_time.get("url")
#
#         try:
#
#             if not MESSAGES.get(message_key):
#                 logging.error(f"Сообщение {message_key} не найдено, не направлено юзеру: {user_id}")
#                 return
#             else:
#                 message = MESSAGES.get(message_key).format(user_name, url) if url else MESSAGES.get(message_key).format(user_name)
#
#                 if image:
#                     image_path = os.path.join("app", "images", f"{message_key}.jpg")
#                     if not os.path.exists(image_path):
#                         logging.error(f"Изображение {image_path} не найдено")
#                     else:
#                         image = FSInputFile(image_path)
#                         await bot.send_photo(user_id, image)  # Отправляем изображение
#                         logging.info(f"{message_key} изображение отправлено пользователю {user_id}")
#
#                 if audio:
#                     audio_path = os.path.join("app", "audio", f"{message_key}.mp3")
#                     if not os.path.exists(audio_path):
#                         logging.error(f"Аудиофайл {audio_path} не найден")
#                         await bot.send_message(user_id, message)  # Отправляем только текст
#                         logging.info(f"{message_key} текст без аудио отправлен пользователю {user_id}")
#                     else:
#                         audio = FSInputFile(audio_path)
#                         await bot.send_audio(user_id, audio, caption=message, title=date_time.get("audio_name"))  # Отправляем изображение c тексом
#                         logging.info(f"{message_key} текст с аудио отправлен пользователю {user_id}")
#                 else:
#                     await bot.send_message(user_id, message)  # Отправляем только текст
#                     logging.info(f"{message_key} текст отправлен пользователю {user_id}")
#
#                 # if date_time.get("add_question"):
#                 #     # Создаем новый контекст состояния
#                 #     storage = MemoryStorage()  # Используйте то же хранилище, что и в основном боте
#                 #     state = FSMContext(
#                 #         storage=storage,
#                 #         key=StorageKey(
#                 #             chat_id=user_id,
#                 #             user_id=user_id,
#                 #             bot_id=bot.id
#                 #         )
#                 #     )
#                 #     try:
#                 #         # Явно устанавливаем начальное состояние
#                 #         await state.set_state(FinalQuestions.waiting_for_is_useful)
#                 #         await bot.send_message(user_id, MESSAGES.get("is_useful"))
#                 #         logging.info(f"Опрос начат для {user_id}, состояние установлено")
#                 #     except Exception as e:
#                 #         logging.error(f"Ошибка запуска опроса: {e}")
#                 #     finally:
#                 #         # Не очищаем состояние здесь - оно нужно для последующих сообщений
#                 #         pass
#
#         except Exception as e:
#             logging.error(f"Ошибка отправки уведомления пользователю {user_id}: {e}")
#             #await delete_user(user_id)  # Удаляем, если пользователь недоступен
#
#     else:
#         logging.error(f"Пользователь {user_id} не найден в базе данных, отправка {message_key} не возможна")
#
# async def schedule_single_messages(bot: Bot, user_id: int):
#     for date_time in timetable_single_messages:
#         # добавить сравнение с текущей датой, добавление последующих
#         message_key = date_time.get("message_key")
#         time = date_time.get("time") if date_time.get("time") else {}
#         if time:
#             scheduler.add_job(
#                 send_single_message,
#                 trigger=CronTrigger(
#                     **time,
#                     timezone=ZoneInfo("Europe/Moscow")
#                 ),
#                 args=[bot, user_id, date_time],
#                 max_instances=1,
#                 replace_existing=True,
#                 id=f"{message_key}_{user_id}"  # Уникальный ID для задачи
#             )
#             logging.info(f"Уведомление {message_key} запланировано для пользователя {user_id} на {time}")
#
# async def restore_scheduled_jobs(bot: Bot):
#     """
#     Восстанавливает запланированные задачи из базы данных при перезапуске бота.
#
#     Args:
#         bot: Экземпляр бота для отправки сообщений.
#     """
#     active_users = await get_active_users()
#     for user_id, selected_time in active_users:
#         await schedule_tasks(bot, user_id, selected_time, start_date=START_DAY)
#         await schedule_single_messages(bot, user_id)
#         pass
#
#     logging.info(f"Восстановлено {len(active_users)} задач из базы данных")