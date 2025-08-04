from aiogram.utils.keyboard import InlineKeyboardBuilder

times = ["08:00", "10:00", "12:00", "18:00"]

def get_time_keyboard():
    builder = InlineKeyboardBuilder()
    for time in times:
        builder.button(text=time, callback_data=time)
    builder.adjust(2)
    return builder.as_markup()