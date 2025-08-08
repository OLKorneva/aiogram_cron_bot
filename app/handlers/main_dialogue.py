"""
Модуль с обработчиками команд и сообщений для Telegram-бота.
Обрабатывает команду /start, выбор времени и ответы на четыре вопроса.
"""

import os
from aiogram import Router, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging

from app.messages import MESSAGES, START_DAY
from app.filters import TimeFilter
from app.scheduler import scheduler, schedule_single_messages, schedule_tasks
from app.database import save_user_data, get_user_data, save_final_answer
import app.keyboards as kb
from app.utils import get_formated_day

router = Router()


# FSM для сбора ответов
class UserForm(StatesGroup):
    waiting_for_question_name = State()
    waiting_for_question_goal = State()
    waiting_for_question_screen_time = State()
    waiting_for_time = State()

# FSM для сбора ответов
class FinalQuestions(StatesGroup):
    waiting_for_is_useful = State()
    waiting_for_whats_new = State()
    waiting_for_whats_changed = State()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    logging.info(f"Получена команда /start от пользователя {message.from_user.id}")
    photo = FSInputFile(os.path.join("app", "images", "start.jfif"))
    await message.answer_photo(photo=photo, caption=MESSAGES["start"])
    await message.answer(text=MESSAGES["question_name"])
    await state.set_state(UserForm.waiting_for_question_name)

@router.message(UserForm.waiting_for_question_name)
async def process_question_name(message: Message, state: FSMContext) -> None:
    await state.update_data(user_name=message.text.strip())
    await message.answer(MESSAGES["question_goal"])
    await state.set_state(UserForm.waiting_for_question_goal)

@router.message(UserForm.waiting_for_question_goal)
async def process_question_goal(message: Message, state: FSMContext) -> None:
    await state.update_data(goal=message.text)
    await message.answer(MESSAGES["question_screen_time"], reply_markup=kb.get_screen_time_keyboard())
    await state.set_state(UserForm.waiting_for_question_screen_time)

@router.callback_query(TimeFilter(kb.screen_time), UserForm.waiting_for_question_screen_time)
async def process_question_screen_time(callback: CallbackQuery, state: FSMContext) -> None:
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
    selected_time = callback.data
    user_id = callback.from_user.id
    logging.info(f"Пользователь {user_id} выбрал время {selected_time}")

    # Получаем данные из state
    data = await state.get_data()
    user_name = data.get("user_name")
    goal = data.get("goal", "")
    screen_time = data.get("screen_time", "")
    start_date = START_DAY
    days_left = 16

    # Сохранение данных в базу
    await save_user_data(user_id, user_name, selected_time, goal, screen_time, start_date, days_left)

    # Планирование уведомлений
    await schedule_single_messages(callback.bot, user_id)
    await schedule_tasks(callback.bot, user_id, selected_time, start_date)

    try:
        await callback.message.edit_text(
            MESSAGES["selected"].format(get_formated_day(start_date), selected_time),
            reply_markup=None)
    except Exception as e:
        logging.error(f"Ошибка при редактировании сообщения: {e}")
        await callback.message.answer(MESSAGES["selected"])
    await callback.answer(f'Вы выбрали {callback.data}')

    # Очистка состояния
    await state.clear()
    logging.info(f"Пользователь {user_id} завершил опрос: время={selected_time}, ответы=({user_name}, {goal}, {screen_time}, {selected_time})")

    # Подтверждение callback
    await callback.answer(f"Вы выбрали {selected_time}")


