from aiogram import Router, Bot

from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
import logging

from app.filters import KeyFilter
from app.handlers.start_dialogue import CHANNEL_ID
from app.keyboards import get_text_by_id
from app.messages import dialogue_messages, questions, confirms
from app.database import get_user_data, save_user_data
from aiogram.filters import Command
import app.keyboards as kb
from app.utils.audio import send_audio_challenge
from app.utils.form import UserForm

router = Router()

@router.callback_query(KeyFilter(kb.feedback), UserForm.waiting_for_feedback)
async def process_feedback(callback: CallbackQuery, state: FSMContext) -> None:
    feedback = get_text_by_id(callback.data, kb.feedback_options, kb.feedback_ids)
    try:
        await save_user_data(callback.from_user.id, feedback=feedback)
        logging.info(f'Отзыв пользователя {callback.from_user.id} сохранен в базу данных')
    except Exception as e:
        logging.error(f'Ошибка сохранения отзыва пользователя {callback.from_user.id}: {e}')

    try:
        await callback.message.edit_text(confirms.get('feedback'), reply_markup=None)
    except Exception as e:
        logging.error(f'Ошибка редактирования вопроса об отзыве у пользователя {callback.from_user.id}: {e}')
        await callback.message.answer(confirms.get('feedback'))
    finally:
        await state.clear()

@router.callback_query(KeyFilter(kb.screen_time), UserForm.waiting_for_after_screen_time)
async def process_after_screen_time(callback: CallbackQuery, state: FSMContext) -> None:
    after_screen_time = kb.get_text_by_id(callback.data, kb.screen_time_options, kb.screen_time_ids)
    await save_user_data(callback.from_user.id, after_screen_time=after_screen_time)
    try:
        data = await get_user_data(callback.from_user.id)
        screen_time = data.get('screen_time')
        if screen_time:
            await callback.message.edit_text(
              confirms.get('after_screen_time').format(screen_time, after_screen_time), reply_markup=None)
        else:
            logging.error(f"Не найдены данные об экранном времени пользователя {callback.from_user.id}")
            await callback.message.edit_text(
                confirms.get('screen_time').format(after_screen_time), reply_markup=None)
        logging.info(f"Обработано экранное время, введенное пользователем {callback.from_user.id}")
    except Exception as e:
        logging.error(f"Ошибка при редактировании сообщения пользователя {callback.from_user.id} об экранном времени: {e}")
        await callback.message.answer(
            confirms.get('screen_time').format(after_screen_time), reply_markup=None)

    await callback.message.answer(text=questions.get('after_focus'), reply_markup=kb.get_focuses_keyboard())
    await state.set_state(UserForm.waiting_for_after_focus)

@router.callback_query(KeyFilter(kb.focuses), UserForm.waiting_for_after_focus)
async def process_after_focus(callback: CallbackQuery, state: FSMContext) -> None:
    try:
        after_focus = kb.get_text_by_id(callback.data, kb.focus_options, kb.focus_ids)
        await save_user_data(callback.from_user.id, after_focus=after_focus)

        data = await get_user_data(callback.from_user.id)
        old_focus_text = data.get('focus')
        if old_focus_text:
            await callback.message.edit_text(
                confirms.get('after_focus').format(old_focus_text, after_focus), reply_markup=None)
        else:
            logging.error(f"Не найдены данные о фокусе пользователя {callback.from_user.id}")
            await callback.message.edit_text(
                confirms.get('focus').format(after_focus), reply_markup=None)
    except Exception as e:
        logging.error(f"Ошибка при обработке сообщения пользователя {callback.from_user.id} о фокусе: {e}")

    await callback.message.answer(text=questions.get('is_useful'), reply_markup=kb.get_useful_keyboard())
    await state.set_state(UserForm.waiting_for_is_useful)

@router.callback_query(KeyFilter(kb.useful), UserForm.waiting_for_is_useful)
async def process_question_is_useful(callback: CallbackQuery, state: FSMContext) -> None:
    try:
        is_useful = kb.get_text_by_id(callback.data, kb.useful_options, kb.useful_ids)
        await save_user_data(callback.from_user.id, is_useful=is_useful)
        await callback.message.edit_text(confirms.get('useful'), reply_markup=None)
        logging.info(f"Пользователь {callback.from_user.id} ответил на вопрос о полезности")
    except Exception as e:
        logging.error(f"Ошибка обработки ответа is_useful: {e}")
        #await state.clear()

    await callback.message.answer(text=questions.get('whats_new'), reply_markup=None)
    await state.set_state(UserForm.waiting_for_whats_new)

@router.message(UserForm.waiting_for_whats_new)
async def process_question_whats_new(message: Message, state: FSMContext) -> None:
    try:
        await save_user_data(message.from_user.id, whats_new=message.text.strip())
        logging.info(f"Пользователь {message.from_user.id} ответил на вопрос о новом")
    except Exception as e:
        logging.error(f"Ошибка обработки ответа whats_new: {e}")
        #await state.clear()

    await message.answer(text=questions.get('whats_changed'), reply_markup=kb.get_changes_keyboard())
    await state.set_state(UserForm.waiting_for_whats_changed)

@router.callback_query(KeyFilter(kb.changes), UserForm.waiting_for_whats_changed)
async def process_question_whats_changed(callback: CallbackQuery, state: FSMContext) -> None:
    whats_changed = kb.get_text_by_id(callback.data, kb.changes_options, kb.changes_ids)
    await save_user_data(callback.from_user.id, whats_changed=whats_changed)

    try:
        await callback.message.edit_text(confirms.get('changed'), reply_markup=None)
    except Exception:
        await callback.message.answer(confirms.get('changed'), reply_markup=None)

    try:
        old_data = await get_user_data(callback.from_user.id)
        changes = old_data.get('changes')
        if changes:
            await callback.message.answer(text=confirms.get('after_changed').format(changes))
        else:
            logging.error(f"Не найдены данные о желаемых изменениях пользователя {callback.from_user.id}")
    except Exception as e:
        logging.error(f"Ошибка отправки пользователю {callback.from_user.id} напоминания о его целях: {e}")


    await callback.message.answer(text=questions.get('else_challenge'), reply_markup=kb.get_else_challenge_keyboard())
    await state.set_state(UserForm.waiting_for_else_challenge)


@router.callback_query(KeyFilter(kb.else_challenge), UserForm.waiting_for_else_challenge)
async def process_question_else_challenge(callback: CallbackQuery, state: FSMContext) -> None:
    try:
        else_challenge = kb.get_text_by_id(callback.data, kb.else_challenge_options, kb.else_challenge_ids)
        await save_user_data(callback.from_user.id, else_challenge=else_challenge)
    except Exception as e:
        logging.error(f"Ошибка обработки ответа else_challenge у {callback.from_user.id}: {e}")

    try:
        if callback.data == "else_2":
            await callback.message.answer(confirms.get('save_final_result'))
            await state.clear()
        else:
            await callback.message.answer(questions.get('topics'))
            await state.set_state(UserForm.waiting_for_topics)

    except Exception as e:
        logging.error(f"Ошибка обработки ответа else_challenge: {e}")


@router.message(UserForm.waiting_for_topics)
async def process_question_topics(message: Message, state: FSMContext) -> None:
    try:
        await save_user_data(message.from_user.id, topics=message.text.strip())
        logging.info(f"Пользователь {message.from_user.id} ответил на вопрос о темах челленджей")
    except Exception as e:
        logging.error(f"Ошибка обработки ответа пользователя {message.from_user.id} о новых челленджах: {e}")
    finally:
        await state.clear()

    await message.answer(confirms.get('save_final_result'))
