from aiogram import Router, Bot

from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging

from app.filters import KeyFilter
from app.handlers.main_dialogue import UserForm, CHANNEL_ID
from app.messages import MESSAGES, dialogue_messages, questions, confirms
from app.database import save_final_answer, get_user_data
from aiogram.filters import Command
import app.keyboards as kb

router = Router()


@router.message(Command("final"))
async def final_questions(message: Message, bot: Bot, state: FSMContext):
    try:
        await bot.forward_message(
            chat_id=message.from_user.id,
            from_chat_id=CHANNEL_ID,
            message_id=dialogue_messages.get('final_questions_start', {}).get('forward_key')
        )
        await message.answer(questions.get('screen_time'), reply_markup=kb.get_screen_time_keyboard())
        await state.set_state(UserForm.waiting_for_after_screen_time)

    except Exception as e:
        logging.error(f"Ошибка пересылки пользователю {message.from_user.id} сообщения с финальными вопросами: {e} ")
    logging.info(f"Начат финальный опрос пользователя {message.from_user.id}")

@router.callback_query(KeyFilter(kb.screen_time), UserForm.waiting_for_after_screen_time)
async def process_after_screen_time(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(after_screen_time=callback.data)
    try:
        data = await get_user_data(callback.from_user.id)
        screen_time = data['screen_time']
        if screen_time:
            was = kb.get_text_by_id(screen_time, kb.screen_time_options, kb.screen_time_ids)
            new = kb.get_text_by_id(callback.data, kb.screen_time_options, kb.screen_time_ids)
            await callback.message.edit_text(
              confirms.get('after_screen_time').format(was, new), reply_markup=None)
        else:
            await callback.message.edit_text(
                questions.get('confirm_screen_time').format(callback.data), reply_markup=None)
    except Exception as e:
        logging.error(f"Ошибка при редактировании сообщения пользователя {callback.from_user.id} об экранном времени: {e}")
        await callback.message.answer(questions.get('confirm_screen_time').format(callback.data))

    await callback.message.answer(text=questions.get('focus'), reply_markup=kb.get_focuses_keyboard())
    await state.set_state(UserForm.waiting_for_after_focus)
    logging.info(f"Обработано экранное время, введенное пользователем {callback.from_user.id}")

@router.callback_query(KeyFilter(kb.focuses), UserForm.waiting_for_after_focus)
async def process_after_focus(callback: CallbackQuery, state: FSMContext) -> None:
    try:
        await state.update_data(after_focus=callback.data.strip())

        data = await get_user_data(callback.from_user.id)
        focus_ind = data['focus']
        focus_text = kb.get_text_by_id(focus_ind, kb.focus_options, kb.focus_ids)
        if focus_text:
            await callback.message.answer(text=confirms.get('after_focus').format(focus_text))
        else:
            logging.error(f"Не найдены данные о фокусе пользователя {callback.from_user.id}")

        await callback.message.answer(text=questions.get('is_useful'), reply_markup=kb.get_useful_keyboard())
        await state.set_state(UserForm.waiting_for_is_useful)
    except Exception as e:
        logging.error(f"Ошибка при обработке сообщения пользователя {callback.from_user.id} о фокусе: {e}")

@router.callback_query(KeyFilter(kb.useful), UserForm.waiting_for_is_useful)
async def process_question_is_useful(callback: CallbackQuery, state: FSMContext) -> None:
    try:
        await state.update_data(is_useful=callback.data)
        await callback.message.answer(text=questions.get('whats_new'), reply_markup=None)
        await state.set_state(UserForm.waiting_for_whats_new)
        logging.info(f"Пользователь {callback.from_user.id} ответил на первый вопрос")
    except Exception as e:
        logging.error(f"Ошибка обработки ответа is_useful: {e}")
        #await state.clear()

@router.message(UserForm.waiting_for_whats_new)
async def process_question_whats_new(message: Message, state: FSMContext) -> None:
    try:
        await state.update_data(whats_new=message.text)
        await message.answer(text=questions.get('whats_changed'))
        await state.set_state(UserForm.waiting_for_whats_changed)
        logging.info(f"Пользователь {message.from_user.id} ответил на второй вопрос")
    except Exception as e:
        logging.error(f"Ошибка обработки ответа whats_new: {e}")
        #await state.clear()

@router.message(UserForm.waiting_for_whats_changed)
async def process_question_whats_changed(message: Message, state: FSMContext) -> None:
    try:
        last_data = await get_user_data(message.from_user.id)
        changes = last_data.get('changes')
        if changes:
            await message.answer(text=confirms.get('after_changed').format(changes))
        else:
            logging.error(f"Не найдены данные о желаемых изменениях пользователя {message.from_user.id}")

        user_id = message.from_user.id

        # Получаем все сохраненные ответы
        data = await state.get_data()
        after_screen_time = data.get('after_screen_time')
        after_focus = data.get('after_focus')
        is_useful = data.get('is_useful')
        whats_new = data.get('whats_new')
        whats_changed = message.text


        # Сохраняем в базу данных
        await save_final_answer(
            user_id=user_id,
            after_screen_time=after_screen_time,
            after_focus=after_focus,
            is_useful=is_useful,
            whats_new=whats_new,
            whats_changed=whats_changed
        )

        await message.answer('Спасибо! Ваши ответы сохранены!')
        logging.info(
            f"Пользователь {user_id} завершил опрос. "
            f"Ответы: полезность={is_useful}, новое={whats_new}, изменения={whats_changed}, "
            f"экранное время: {after_screen_time}, фокус: {after_focus}")

    except Exception as e:
        logging.error(f"Ошибка сохранения финальных ответов пользователя {user_id}: {e}")
        await message.answer("Произошла ошибка при сохранении ответов")
    finally:
        await state.clear()