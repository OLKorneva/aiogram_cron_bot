from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from app.messages import timetable_single_messages
from app.scheduler import scheduler, send_task, send_single_message
from app.database import get_user_data, get_active_users
from aiogram import Router, Bot, F


router = Router()


@router.message(Command("get_me"))
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

@router.message(Command("get_all"))
async def cmd_get_all(message: Message) -> None:
    user_id = message.from_user.id
    data = await get_user_data(user_id)
    if data:
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
            await message.answer('В челлендже пока никто не зарегистирован.')
    else:
        await message.answer("Вы не зарегистрированы в челлендже, пройдите регистрацию /start!")

@router.message(Command("all_task_day"))
async def cmd_all_task_day(message: Message) -> None:
    user_id = message.from_user.id
    data = await get_user_data(user_id)
    if data:
        selected_time = data.get("selected_time")
        for i in range(1, 16):
            #await message.answer(f"Следующее сообщение будет направлено {i + 4} сентября в {selected_time}")
            await send_task(bot=message.bot, user_id=user_id, day_num=i)
    else:
        await message.answer("Вы не зарегистрированы в челлендже, пройдите регистрацию /start!")


@router.message(Command("all_single_messages"))
async def cmd_all_single_messages(message: Message) -> None:
    user_id = message.from_user.id
    data = await get_user_data(user_id)
    if data:
        for date_time in timetable_single_messages:
            time = date_time.get("time")
            await message.answer(f'Следующее сообщение будет направлено: {time}')
            await send_single_message(bot=message.bot, user_id=message.from_user.id, date_time=date_time)
    else:
        await message.answer("Вы не зарегистрированы в челлендже, пройдите регистрацию /start!")

@router.message(Command("list_jobs"))
async def cmd_list_jobs(message: Message) -> None:
    user_id = message.from_user.id
    data = await get_user_data(user_id)
    if data:
        jobs = scheduler.get_jobs()
        if jobs:
            job_info = "\n".join([f"Job ID: {job.id}, Next run: {job.next_run_time}" for job in jobs])
            await message.answer(f"Запланированные задачи:\n{job_info}")
        else:
            await message.answer("Нет запланированных задач.")
    else:
        await message.answer("Вы не зарегистрированы в челлендже, пройдите регистрацию /start!")

id_chanel = -1002942800483
@router.message(Command("check"))
async def cmd_check(message: Message, bot: Bot) -> None:
    await bot.forward_message(
        chat_id=message.from_user.id,
        from_chat_id=id_chanel,
        message_id=2
    )