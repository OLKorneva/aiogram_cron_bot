"""
Модуль с обработчиками команд и сообщений для Telegram-бота.
Обрабатывает команду /start, выбор времени и ответы на четыре вопроса.
"""

from aiogram import Router, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import logging
from dotenv import load_dotenv

from app.messages import dialogue_messages, questions, confirms, CHANNEL_ID
from app.filters import KeyFilter
from app.scheduler import add_new_user_to_schedule
from app.database import save_user_data, get_name
import app.keyboards as kb
from app.utils.context import dp_var
from app.utils.form import UserForm
from app.utils.retry import retry_async

router = Router()
load_dotenv()

@router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot, state: FSMContext) -> None:
    await state.clear()
    user_id = message.from_user.id
    logging.info(f"Получена команда /start от пользователя {user_id} c именем {message.from_user.first_name}")

    forward_key = dialogue_messages.get('start', {}).get('forward_key')

    async def forward_first_message():
        await bot.forward_message(
            chat_id=user_id,
            from_chat_id=CHANNEL_ID,
            message_id=forward_key
        )

    try:
        # Ретрай пересылки сообщения
        await retry_async(forward_first_message)

        await state.set_state(UserForm.waiting_for_question_name)

        # После успешной пересылки
        await message.answer(text=questions.get('name'))
        logging.info(f"Пользователю {user_id} направлено первое сообщение")

    except Exception as e:
        # Логируем ошибку, но не тревожим пользователя
        logging.error(f"Не удалось отправить первое сообщение пользователю {user_id} после ретраев: {e}")


@router.message(UserForm.waiting_for_question_name)
async def process_question_name(message: Message, state: FSMContext) -> None:
    user_name = message.text.strip()
    try:
        await save_user_data(message.from_user.id, user_name=user_name)
        await message.reply(confirms.get('name').format(user_name))
        await message.answer(questions.get('screen_time'), reply_markup=kb.get_screen_time_keyboard())
        await state.set_state(UserForm.waiting_for_question_screen_time)
    except Exception as e:
        logging.error(f"Ошибка обработки введенного пользователем {message.from_user.id} имени: {e}")
        await message.message.answer("Произошла ошибка. Попробуйте еще раз.")
    logging.info(f"Обработано имя, введенное пользователем {message.from_user.id}")

@router.callback_query(KeyFilter(kb.screen_time), UserForm.waiting_for_question_screen_time)
async def process_question_screen_time(callback: CallbackQuery, state: FSMContext) -> None:
    try:
        screen_time_text = kb.get_text_by_id(callback.data, kb.screen_time_options, kb.screen_time_ids)
        await save_user_data(callback.from_user.id, screen_time=screen_time_text)

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
        logging.info(f"Обработано экранное время пользователя {callback.from_user.id}: {screen_time_text}")

    except Exception as e:
        logging.error(f"Ошибка обработки экранного времени пользователя {callback.from_user.id}: {e}")
        await callback.message.answer("Произошла ошибка. Попробуйте еще раз.")

@router.callback_query(KeyFilter(kb.focuses), UserForm.waiting_for_question_focus)
async def process_question_focus(callback: CallbackQuery, state: FSMContext) -> None:
    try:
        focus_text = kb.get_text_by_id(callback.data, kb.focus_options, kb.focus_ids)
        await save_user_data(callback.from_user.id, focus=focus_text)

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

@router.message(UserForm.waiting_for_question_changes)
async def process_question_changes(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id

    try:
        changes=message.text
        user_name = await get_name(user_id)

        await message.answer(confirms.get('save_first_result').format(user_name))

        # Сохранение данных в базу
        await save_user_data(message.from_user.id, changes=changes)
        logging.info(f"Пользователь {user_id} завершил опрос")
        logging.info(f"Обработаны данные о желаемых изменениях, введенные пользователем {message.from_user.id}")

        # Планирование уведомлений
        await add_new_user_to_schedule(message.bot, user_id, dp_var.get())



    except Exception as e:
        logging.error(f"Ошибка при обработке и сохранении результатов опроса пользователя {message.from_user.id}: {e}")
    finally:
        await state.clear()  # Очистка состояния после успешного сохранения
