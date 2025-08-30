from os import getenv

from aiogram.filters import Command, BaseFilter
from aiogram.types import Message
from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext

from app.messages import timetable_single_messages
from app.scheduler import scheduler, send_single_message_safe, run_final_questions, run_middle_question
from app.database import get_user_data, get_active_users


# ======================
# Фильтр только для админа
# ======================
ADMIN_ID = int(getenv("ADMIN_ID", 0))


class IsAdmin(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id == ADMIN_ID


# ======================
# Роутер админских команд
# ======================
admin_router = Router()
admin_router.message.filter(IsAdmin())


# ======================
# Хендлеры только для админа
# ======================

@admin_router.message(Command("middle"))
async def middle_question(message: Message, bot: Bot, state: FSMContext):
    await run_middle_question(bot, message.from_user.id, state)

@admin_router.message(Command("final"))
async def final_questions(message: Message, bot: Bot, state: FSMContext):
    await run_final_questions(bot, message.from_user.id, state)

@admin_router.message(Command("get_me"))
async def cmd_get_me(message: Message) -> None:
    user_id = message.from_user.id
    data = await get_user_data(user_id)
    if data:
        try:
            response = f"Данные пользователя: {data}"
        except UnicodeEncodeError:
            response = f"Данные пользователя: {tuple(str(item).encode('utf-8', errors='replace').decode('utf-8') for item in data)}"
        await message.answer(response)
    else:
        await message.answer("Вы не зарегистрированы в челлендже, пройдите регистрацию /start!")


@admin_router.message(Command("get_all"))
async def cmd_get_all(message: Message) -> None:
    user_list = await get_active_users()
    id_list = [user_id for user_id, _ in user_list]
    registrated = []

    for user_id in id_list:
        data = await get_user_data(user_id)
        if data:
            try:
                response = f"Данные пользователя: {data}"
            except UnicodeEncodeError:
                response = f"Данные пользователя: {tuple(str(item).encode('utf-8', errors='replace').decode('utf-8') for item in data)}"
            registrated.append(response)

    if registrated:
        await message.answer('\n\n'.join(registrated))
    else:
        await message.answer('В челлендже пока никто не зарегистрирован.')


@admin_router.message(Command("all_single_messages"))
async def cmd_all_single_messages(message: Message) -> None:
    user_id = message.from_user.id
    data = await get_user_data(user_id)
    if data:
        for date_time in timetable_single_messages:
            time = date_time.get("time")
            await message.answer(f'Следующее сообщение будет направлено: {time}')
            message_key = date_time.get("message_key")
            if message_key in ['final', 'middle']:
                continue
            await send_single_message_safe(bot=message.bot, user_id=message.from_user.id, date_time=date_time)
    else:
        await message.answer("Вы не зарегистрированы в челлендже, пройдите регистрацию /start!")


@admin_router.message(Command("list_jobs"))
async def cmd_list_jobs(message: Message) -> None:
    jobs = scheduler.get_jobs()
    if jobs:
        job_info = "\n".join([f"Job ID: {job.id}, Next run: {job.next_run_time}" for job in jobs])
        await message.answer(f"Запланированные задачи:\n{job_info}")
    else:
        await message.answer("Нет запланированных задач.")


# @admin_router.message(F.audio)
# async def get_file_id(msg: Message):
#     await msg.answer(f"file_id: {msg.audio.file_id}")
#
# @admin_router.message()
# async def get_file_id(msg: Message):
#     await msg.answer(f"file_id: {msg.message_id}")



# @router.message(Command("final"))
# async def final_questions(message: Message, bot: Bot, state: FSMContext):
#     try:
#         await bot.forward_message(
#             chat_id=message.from_user.id,
#             from_chat_id=CHANNEL_ID,
#             message_id=dialogue_messages.get('final_questions_start', {}).get('forward_key')
#         )
#         await message.answer(questions.get('after_screen_time'), reply_markup=kb.get_screen_time_keyboard())
#         await state.set_state(UserForm.waiting_for_after_screen_time)
#
#     except Exception as e:
#         logging.error(f"Ошибка пересылки пользователю {message.from_user.id} сообщения с финальными вопросами: {e} ")
#     logging.info(f"Начат финальный опрос пользователя {message.from_user.id}")