"""
Модуль с обработчиками команд и сообщений для Telegram-бота.
Обрабатывает команду /start, выбор времени и ответы на четыре вопроса.
"""
import aiosqlite
import asyncio
from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging
import aiohttp
from datetime import datetime, timedelta
from app.keyboards import get_time_keyboard
from app.messages import MESSAGES
from app.filters import TimeFilter
from app.scheduler import schedule_notification, send_notification, scheduler
from app.database import save_user_data, get_user_data
import app.keyboards as kb

router = Router()


# FSM для сбора ответов
class UserForm(StatesGroup):
    waiting_for_time = State()
    waiting_for_question1 = State()
    waiting_for_question2 = State()
    waiting_for_question3 = State()
    waiting_for_question4 = State()

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
    user_name = message.from_user.last_name or message.from_user.first_name or ""
    await message.answer(
        text=MESSAGES["start"].format(user_name),
        reply_markup=get_time_keyboard()
    )
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
    logging.info(f"Пользователь {callback.from_user.id} выбрал время {selected_time}")
    await state.update_data(selected_time=selected_time)
    try:
        await callback.message.edit_text(
            MESSAGES["selected"].format(selected_time),
            reply_markup=None
        )
    except Exception as e:
        logging.error(f"Ошибка при редактировании сообщения: {e}")
        await callback.message.answer(MESSAGES["selected"].format(selected_time))
    await callback.message.answer(MESSAGES["question1"])
    await state.set_state(UserForm.waiting_for_question1)
    await callback.answer(f"Вы выбрали {selected_time}")

    # Объединяем ответы в одно сообщение, чтобы сократить API-запросы
    # try:
    #     await callback.message.answer(
    #         f"{MESSAGES['selected'].format(selected_time)}\n{MESSAGES['question1']}"
    #     )
    #     await callback.message.delete()  # Удаляем сообщение с клавиатурой
    #     await callback.answer(f"Вы выбрали {selected_time}")
    #     await state.set_state(UserForm.waiting_for_question1)
    # except (aiohttp.ClientError, asyncio.TimeoutError) as e:
    #     logging.error(f"Ошибка отправки сообщения в set_time: {e}")
    #     await callback.message.answer("Произошла сетевая ошибка. Пожалуйста, попробуйте снова.")
    #     await callback.answer("Ошибка сети")

@router.message(UserForm.waiting_for_question1)
async def process_question1(message: Message, state: FSMContext) -> None:
    """
    Обработчик ответа на первый вопрос.
    Сохраняет ответ и запрашивает второй вопрос.

    Args:
        message: Входящее сообщение с ответом.
        state: Контекст FSM для хранения данных.
    """
    await state.update_data(answer1=message.text)
    await message.answer(MESSAGES["question2"])
    await state.set_state(UserForm.waiting_for_question2)

@router.message(UserForm.waiting_for_question2)
async def process_question2(message: Message, state: FSMContext) -> None:
    """
    Обработчик ответа на второй вопрос.
    Сохраняет ответ и запрашивает третий вопрос.

    Args:
        message: Входящее сообщение с ответом.
        state: Контекст FSM для хранения данных.
    """
    await state.update_data(answer2=message.text)
    await message.answer(MESSAGES["question3"])
    await state.set_state(UserForm.waiting_for_question3)

@router.message(UserForm.waiting_for_question3)
async def process_question3(message: Message, state: FSMContext) -> None:
    """
    Обработчик ответа на третий вопрос.
    Сохраняет ответ и запрашивает четвёртый вопрос.

    Args:
        message: Входящее сообщение с ответом.
        state: Контекст FSM для хранения данных.
    """
    await state.update_data(answer3=message.text)
    await message.answer(MESSAGES["question4"])
    await state.set_state(UserForm.waiting_for_question4)

@router.message(UserForm.waiting_for_question4)
async def process_question4(message: Message, state: FSMContext) -> None:
    """
    Обработчик ответа на четвёртый вопрос.
    Сохраняет все данные в базу, планирует уведомления и завершает опрос.

    Args:
        message: Входящее сообщение с ответом.
        state: Контекст FSM для хранения данных.
    """
    user_id = message.from_user.id
    data = await state.get_data()
    selected_time = data["selected_time"]
    answer1 = data["answer1"]
    answer2 = data["answer2"]
    answer3 = data["answer3"]
    answer4 = message.text
    start_date = datetime.now().date() + timedelta(days=1)
    days_left = 15

    # Сохранение данных в базу
    await save_user_data(user_id, selected_time, answer1, answer2, answer3, answer4, str(start_date), days_left)

    # Планирование уведомлений
    await schedule_notification(message.bot, user_id, selected_time)

    await message.answer(MESSAGES["saved"])
    await state.clear()
    logging.info(f"Пользователь {user_id} завершил опрос: время={selected_time}, ответы=({answer1}, {answer2}, {answer3}, {answer4})")


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
        async with aiosqlite.connect("bot.db") as conn:
            cursor = await conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            user_data = await cursor.fetchone()
        try:
            response = f"Данные пользователя: {user_data}"
        except UnicodeEncodeError:
            response = f"Данные пользователя: {tuple(str(item).encode('utf-8', errors='replace').decode('utf-8') for item in user_data)}"
        await message.answer(response)
    else:
        await message.answer("Вы не зарегистрированы в марафоне!")

@router.message(Command("send_now"))
async def cmd_send_now(message: Message) -> None:
    """
    Временный хендлер для отладки.
    Отправляет тестовое уведомление немедленно.

    Args:
        message: Входящее сообщение.
    """
    user_id = message.from_user.id
    if await get_user_data(user_id):
        try:
            await send_notification(message.bot, user_id)
            await message.answer("Тестовое уведомление отправлено!")
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            logging.error(f"Ошибка отправки тестового уведомления: {e}")
            await message.answer("Произошла сетевая ошибка при отправке уведомления.")
    else:
        await message.answer("Вы не зарегистрированы в марафоне!")

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
