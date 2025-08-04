from aiogram.utils.keyboard import InlineKeyboardBuilder

times = ["08:00", "10:00", "12:00", "18:00"]

screen_time = ["менее часа", "от часа до двух", "от двух часов до пяти", "от пяти часов до 8 часов", "более 8 часов"]

def get_time_keyboard():
    builder = InlineKeyboardBuilder()
    for time in times:
        builder.button(text=time, callback_data=time)
    builder.adjust(2)
    return builder.as_markup()


def get_screen_time_keyboard():
    builder = InlineKeyboardBuilder()
    for time in screen_time:
        builder.button(text=time, callback_data=time)
    builder.adjust(2)
    return builder.as_markup()