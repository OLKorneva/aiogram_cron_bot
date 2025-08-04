"""
Модуль с обработчиками команд и сообщений для Telegram-бота.
Обрабатывает команду /start, выбор времени и ответы на четыре вопроса.
"""
import aiohttp
import asyncio
from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging
from datetime import datetime, timedelta, date

from app.keyboards import get_time_keyboard
from app.messages import MESSAGES, START_DAY
from app.filters import TimeFilter
from app.scheduler import schedule_notification, send_notification, scheduler
from app.database import save_user_data, get_user_data
import app.keyboards as kb
from app.utils import get_tomorrow_day, get_formated_day

router = Router()


# FSM для сбора ответов
class UserForm(StatesGroup):
    waiting_for_question_name = State()
    waiting_for_question_goal = State()
    waiting_for_question_screen_time = State()
    waiting_for_time = State()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    """
    Обработчик команды /start.
    Отправляет приветственное сообщение с клавиатурой для выбора времени.

    Args:
        message: Входящее сообщение.
        state: Контекст FSM для управления состоянием.
    """
    logging.info(f"Получена команда /start от пользователя {message.from_user.id}")
    photo = FSInputFile("app/images/start.jpg")
    await message.answer_photo(photo=photo, caption=MESSAGES["start"])
    audio = FSInputFile("app/audio/day2.mp3", filename='День_тестовый.mp3')
    await message.answer_audio(
        audio=audio,
        caption="Тестовое аудио"
    )
    await message.answer(text=MESSAGES["question_name"])
    await state.set_state(UserForm.waiting_for_question_name)

@router.message(UserForm.waiting_for_question_name)
async def process_question_name(message: Message, state: FSMContext) -> None:
    """
    Обработчик ответа на первый вопрос.
    Сохраняет ответ и запрашивает второй вопрос.

    Args:
        message: Входящее сообщение с ответом.
        state: Контекст FSM для хранения данных.
    """
    await state.update_data(user_name=message.text.strip())
    await message.answer(MESSAGES["question_goal"])
    await state.set_state(UserForm.waiting_for_question_goal)

@router.message(UserForm.waiting_for_question_goal)
async def process_question_goal(message: Message, state: FSMContext) -> None:
    """
    Обработчик ответа на второй вопрос.
    Сохраняет ответ и запрашивает третий вопрос.

    Args:
        message: Входящее сообщение с ответом.
        state: Контекст FSM для хранения данных.
    """
    await state.update_data(goal=message.text)
    await message.answer(MESSAGES["question_screen_time"], reply_markup=kb.get_screen_time_keyboard())
    await state.set_state(UserForm.waiting_for_question_screen_time)

@router.callback_query(TimeFilter(kb.screen_time), UserForm.waiting_for_question_screen_time)
async def process_question_screen_time(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Обработчик ответа на третий вопрос.
    Сохраняет ответ и запрашивает четвёртый вопрос.

    Args:
        message: Входящее сообщение с ответом.
        state: Контекст FSM для хранения данных.
    """
    await state.update_data(screen_time=callback.data)
    data = await state.get_data()
    user_name = data["user_name"]
    try:
        await callback.message.edit_text(
            MESSAGES["confirm_screen_time"].format(callback.data), reply_markup=None)
    except Exception as e:
        logging.error(f"Ошибка при редактировании сообщения: {e}")
        await callback.message.answer(MESSAGES["confirm_screen_time"].format(callback.data))

    await callback.message.answer(
            MESSAGES["question_time"].format(user_name),
        reply_markup=kb.get_time_keyboard())
    await state.set_state(UserForm.waiting_for_time)

@router.callback_query(TimeFilter(kb.times), UserForm.waiting_for_time)
async def set_time(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Обработчик выбора времени.
    Сохраняет выбранное время, отправляет подтверждение и запрашивает первый вопрос.

    Args:
        callback: Callback-запрос от кнопки времени.
        state: Контекст FSM для хранения данных.
    """
    selected_time = callback.data
    user_id = callback.from_user.id
    logging.info(f"Пользователь {user_id} выбрал время {selected_time}")

    # Получаем данные из state
    data = await state.get_data()
    user_name = data.get("user_name")
    goal = data.get("goal", "")  # Предполагаемые ответы, замените на ваши
    screen_time = data.get("screen_time", "")
    start_date = START_DAY
    days_left = 16

    # Сохранение данных в базу
    await save_user_data(user_id, user_name, selected_time, goal, screen_time, start_date, days_left)

    # Планирование уведомлений
    await schedule_notification(callback.bot, user_id, selected_time)

    try:
        await callback.message.edit_text(
            MESSAGES["selected"].format(get_formated_day(start_date), selected_time),
            reply_markup=None)
    except Exception as e:
        logging.error(f"Ошибка при редактировании сообщения: {e}")
        await callback.message.answer(MESSAGES["selected"].format(get_formated_day(start_date), selected_time))
    await callback.answer(f'Вы выбрали {callback.data}')

    # Очистка состояния
    await state.clear()
    logging.info(f"Пользователь {user_id} завершил опрос: время={selected_time}, ответы=({user_name}, {goal}, {screen_time}, {selected_time})")

    # Подтверждение callback
    await callback.answer(f"Вы выбрали {selected_time}")

@router.message(Command("debug"))
async def cmd_debug(message: Message) -> None:
    """
    Временный хендлер для отладки.
    Показывает данные пользователя в базе.

    Args:
        message: Входящее сообщение.
    """
    user_id = message.from_user.id
    data = await get_user_data(user_id)
    if data:
        try:
            response = f"Данные пользователя: {data}"
        except UnicodeEncodeError:
            response = f"Данные пользователя: {tuple(str(item).encode('utf-8', errors='replace').decode('utf-8') for item in data)}"
        await message.answer(response)
    else:
        await message.answer("Вы не зарегистрированы в марафоне!")

# @router.message(Command("send_now"))
# async def cmd_send_now(message: Message) -> None:
#     """
#     Временный хендлер для отладки.
#     Отправляет тестовое уведомление немедленно.
#
#     Args:
#         message: Входящее сообщение.
#     """
#     user_id = message.from_user.id
#     if await get_user_data(user_id):
#         try:
#             await send_notification(message.bot, user_id)
#             await message.answer("Тестовое уведомление отправлено!")
#         except (aiohttp.ClientError, asyncio.TimeoutError) as e:
#             logging.error(f"Ошибка отправки тестового уведомления: {e}")
#             await message.answer("Произошла сетевая ошибка при отправке уведомления.")
#     else:
#         await message.answer("Вы не зарегистрированы в марафоне!")

@router.message(Command("list_jobs"))
async def cmd_list_jobs(message: Message) -> None:
    """
    Временный хендлер для отладки.
    Показывает все запланированные задачи.

    Args:
        message: Входящее сообщение.
    """
    jobs = scheduler.get_jobs()
    if jobs:
        job_info = "\n".join([f"Job ID: {job.id}, Next run: {job.next_run_time}" for job in jobs])
        await message.answer(f"Запланированные задачи:\n{job_info}")
    else:
        await message.answer("Нет запланированных задач.")
