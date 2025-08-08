from aiogram import Router, Bot

from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging

from app.messages import MESSAGES
from app.database import save_final_answer


router = Router()


# FSM для сбора ответов
class FinalQuestions(StatesGroup):
    waiting_for_is_useful = State()
    waiting_for_whats_new = State()
    waiting_for_whats_changed = State()

async def final_questions(bot: Bot, user_id: int, state: FSMContext):
    """Функция для отправки финальных вопросов пользователю."""
    try:
        await bot.send_message(user_id, MESSAGES.get("is_useful"))
        await state.set_state(FinalQuestions.waiting_for_is_useful)
        logging.info(f"Начат опрос для пользователя {user_id}")
    except Exception as e:
        logging.error(f"Ошибка запуска опроса для {user_id}: {e}")
        raise

@router.message(FinalQuestions.waiting_for_is_useful)
async def process_question_is_useful(message: Message, state: FSMContext) -> None:
    """Обработка ответа на вопрос 'Был ли полезен марафон?'"""
    try:
        await state.update_data(is_useful=message.text)
        await message.answer(MESSAGES.get("whats_new"))
        await state.set_state(FinalQuestions.waiting_for_whats_new)
        logging.info(f"Пользователь {message.from_user.id} ответил на первый вопрос")
    except Exception as e:
        logging.error(f"Ошибка обработки ответа is_useful: {e}")
        await message.answer("Произошла ошибка, попробуйте позже")
        await state.clear()

@router.message(FinalQuestions.waiting_for_whats_new)
async def process_question_whats_new(message: Message, state: FSMContext) -> None:
    """Обработка ответа на вопрос 'Что нового узнал?'"""
    try:
        await state.update_data(whats_new=message.text)
        await message.answer(MESSAGES.get("whats_changed"))
        await state.set_state(FinalQuestions.waiting_for_whats_changed)
        logging.info(f"Пользователь {message.from_user.id} ответил на второй вопрос")
    except Exception as e:
        logging.error(f"Ошибка обработки ответа whats_new: {e}")
        await message.answer("Произошла ошибка, попробуйте позже")
        await state.clear()

@router.message(FinalQuestions.waiting_for_whats_changed)
async def process_question_whats_changed(message: Message, state: FSMContext) -> None:
    """Обработка ответа на вопрос 'Что изменилось?' и сохранение всех ответов"""
    try:
        user_id = message.from_user.id
        await state.update_data(whats_changed=message.text)

        # Получаем все сохраненные ответы
        data = await state.get_data()
        is_useful = data.get("is_useful")
        whats_new = data.get("whats_new")
        whats_changed = message.text

        # Сохраняем в базу данных
        await save_final_answer(
            user_id=user_id,
            is_useful=is_useful,
            whats_new=whats_new,
            whats_changed=whats_changed
        )

        await message.answer('Спасибо! Ваши ответы сохранены!')
        logging.info(f"Пользователь {user_id} завершил опрос. Ответы: полезность={is_useful}, новое={whats_new}, изменения={whats_changed}")

    except Exception as e:
        logging.error(f"Ошибка сохранения финальных ответов пользователя {user_id}: {e}")
        await message.answer("Произошла ошибка при сохранении ответов")
    finally:
        await state.clear()