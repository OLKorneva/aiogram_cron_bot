"""
Модуль с обработчиками команд и сообщений для Telegram-бота.
Обрабатывает команду /start, выбор времени и ответы на четыре вопроса.
"""

import os
from aiogram import Router, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, FSInputFile, MessageEntity
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging
from os import getenv
from dotenv import load_dotenv

from app.messages import MESSAGES, START_DAY, dialogue_messages, questions, confirms
from app.filters import KeyFilter
#from app.scheduler import scheduler, schedule_single_messages, schedule_tasks
from app.database import save_user_data, get_user_data, save_final_answer
import app.keyboards as kb
from app.utils import get_formated_day

router = Router()
load_dotenv()
CHANNEL_ID = getenv("SOURCE_CHAT_ID")

# FSM для сбора ответов
class UserForm(StatesGroup):
    waiting_for_question_name = State()
    waiting_for_question_screen_time = State()
    waiting_for_question_focus = State()
    waiting_for_question_changes = State()
    waiting_for_time = State()

    waiting_for_after_screen_time = State()
    waiting_for_after_focus = State()
    waiting_for_after_changes = State()

    waiting_for_is_useful = State()
    waiting_for_whats_new = State()
    waiting_for_whats_changed = State()

# # FSM для сбора ответов
# class FinalQuestions(StatesGroup):
#     waiting_for_is_useful = State()
#     waiting_for_whats_new = State()
#     waiting_for_whats_changed = State()


@router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot, state: FSMContext) -> None:
    logging.info(f"Получена команда /start от пользователя {message.from_user.id} c именем {message.from_user.first_name}")
    try:
        await bot.forward_message(
            chat_id=message.from_user.id,
            from_chat_id=CHANNEL_ID,
            message_id=dialogue_messages.get('start', {}).get('forward_key')
        )
        await message.answer(text=questions.get('name'))
        await state.set_state(UserForm.waiting_for_question_name)
    except Exception as e:
        logging.error(f"Ошибка пересылки пользователю {message.from_user.id} первого сообщения: {e} ")
    logging.info(f"Пользователю {message.from_user.id} направлено первое сообщение")

@router.message(UserForm.waiting_for_question_name)
async def process_question_name(message: Message, state: FSMContext) -> None:
    try:
        await state.update_data(user_name=message.text.strip())
        await message.answer(questions.get('screen_time'), reply_markup=kb.get_screen_time_keyboard())
        await state.set_state(UserForm.waiting_for_question_screen_time)
    except Exception as e:
        logging.error(f"Ошибка обработки введенного пользователем {message.from_user.id} имени: {e}")
    logging.info(f"Обработано имя, введенное пользователем {message.from_user.id}")

@router.callback_query(KeyFilter(kb.screen_time), UserForm.waiting_for_question_screen_time)
async def process_question_screen_time(callback: CallbackQuery, state: FSMContext) -> None:
    try:
        # Сохраняем ID выбранного варианта
        await state.update_data(screen_time=callback.data)

        # Получаем текст варианта по ID
        screen_time_text = kb.screen_time_options[kb.screen_time_ids.index(callback.data.split('_')[1])]

        try:
            await callback.message.edit_text(
                confirms.get('screen_time').format(screen_time_text),
                reply_markup=None
            )
        except Exception as e:
            logging.error(f"Ошибка при редактировании сообщения: {e}")
            await callback.message.answer(questions.get('confirm_screen_time').format(screen_time_text))

        await callback.message.answer(text=questions.get('focus'), reply_markup=kb.get_focuses_keyboard())
        await state.set_state(UserForm.waiting_for_question_focus)
        logging.info(f"Обработано экранное время пользователя {callback.from_user.id}: {callback.data}")

    except Exception as e:
        logging.error(f"Ошибка обработки экранного времени пользователя {callback.from_user.id}: {e}")
        await callback.message.answer("Произошла ошибка. Попробуйте еще раз.")

@router.callback_query(KeyFilter(kb.focuses), UserForm.waiting_for_question_focus)
async def process_question_focus(callback: CallbackQuery, state: FSMContext) -> None:
    try:
        await state.update_data(focus=callback.data)
        focus_text = kb.get_text_by_id(callback.data, kb.focus_options, kb.focus_ids)
        try:
            await callback.message.edit_text(
                confirms.get('focus').format(focus_text), reply_markup=None)
        except Exception as e:
            logging.error(f"Ошибка при редактировании сообщения пользователя {callback.from_user.id} об экранном времени: {e}")
            await callback.message.answer(questions.get('confirm_screen_time').format(callback.data))

        await callback.message.answer(questions.get('changes'), reply_markup=None)
        await state.set_state(UserForm.waiting_for_question_changes)
        logging.info(f"Обработан фокус пользователя {callback.from_user.id}: {callback.data}")

    except Exception as e:
        logging.error(f"Ошибка при обработке фокуса пользователя {callback.from_user.id}: {e}")
        await callback.message.answer("Произошла ошибка. Попробуйте еще раз.")

# @router.callback_query(KeyFilter(kb.screen_time), UserForm.waiting_for_question_screen_time)
# async def process_question_screen_time(callback: CallbackQuery, state: FSMContext) -> None:
#     await state.update_data(screen_time=callback.data)
#     try:
#         await callback.message.edit_text(
#             questions.get('confirm_screen_time').format(callback.data), reply_markup=None)
#     except Exception as e:
#         logging.error(f"Ошибка при редактировании сообщения пользователя {callback.from_user.id} об экранном времени: {e}")
#         await callback.message.answer(questions.get('confirm_screen_time').format(callback.data))
#
#     await callback.message.answer(text=questions.get('focus'), reply_markup=kb.get_focuses_keyboard())
#     await state.set_state(UserForm.waiting_for_question_focus)
#     logging.info(f"Обработано экранное время, введенное пользователем {callback.from_user.id}")
#
# @router.callback_query(KeyFilter(kb.focuses), UserForm.waiting_for_question_focus)
# async def process_question_focus(callback: CallbackQuery, state: FSMContext) -> None:
#     try:
#         await state.update_data(focus=callback.text.strip())
#         await callback.answer(questions.get('changes'), reply_markup=kb.get_changes_keyboard())
#         await state.set_state(UserForm.waiting_for_question_changes)
#     except Exception as e:
#         logging.error(f"Ошибка при обработке сообщения пользователя {callback.from_user.id} о фокусе: {e}")

@router.message(UserForm.waiting_for_question_changes)
async def process_question_changes(message: Message, bot: Bot, state: FSMContext) -> None:
    try:
        await state.update_data(changes=message.text)
        await bot.forward_message(
            chat_id=message.from_user.id,
            from_chat_id=CHANNEL_ID,
            message_id=dialogue_messages.get('chose_time', {}).get('forward_key'),
        )
        await message.answer(questions.get('time'), reply_markup=kb.get_time_keyboard())
        await state.set_state(UserForm.waiting_for_time)
    except Exception as e:
        logging.error(f"Ошибка при обработке сообщения пользователя {message.from_user.id} о фокусе: {e}")
    logging.info(f"Обработаны данные о желаемых изменениях, введенные пользователем {message.from_user.id}")

@router.callback_query(KeyFilter(kb.time), UserForm.waiting_for_time)
async def set_time(callback: CallbackQuery, bot: Bot, state: FSMContext) -> None:
    selected_time = callback.data
    user_id = callback.from_user.id
    logging.info(f'Пользователь {user_id} выбрал время {selected_time}')

    # Получаем данные из state
    data = await state.get_data()
    user_name = data.get('user_name')
    screen_time = data.get('screen_time', '')
    focus = data.get('focus', '')
    changes = data.get('changes', '')
    start_date = START_DAY
    days_left = 15

    # Сохранение данных в базу
    await save_user_data(user_id, days_left, user_name, screen_time, focus, changes, selected_time, start_date)

    # Планирование уведомлений
    # await schedule_single_messages(callback.bot, user_id)
    # await schedule_tasks(callback.bot, user_id, selected_time, start_date)

    try:
        await callback.message.edit_text(
            confirms.get('time').format(kb.get_text_by_id(selected_time, kb.times, kb.time_ids)),
            reply_markup=None)
    except Exception as e:
        logging.error(f"Ошибка при редактировании сообщения: {e}")
        await callback.message.answer(MESSAGES["selected"])
    await callback.answer(f'Вы выбрали {callback.data}')


    await bot.forward_message(
        chat_id=callback.from_user.id,
        from_chat_id=CHANNEL_ID,
        message_id=dialogue_messages.get('confirm_time', {}).get('forward_key')
    )

    # Очистка состояния
    await state.clear()
    logging.info(f"Пользователь {user_id} завершил опрос: время={selected_time}, ответы=({user_name}, {screen_time}, {focus}, {changes})")

    # Подтверждение callback
    await callback.answer(f"Вы выбрали {selected_time}")


