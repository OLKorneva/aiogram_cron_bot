from aiogram.utils.keyboard import InlineKeyboardBuilder

times = ["08:00", "10:00", "12:00", "18:00"]
time_ids = ["8", "10", "12", "18"]

screen_time_options = [
    "менее часа",
    "от часа до двух",
    "от двух часов до пяти",
    "от пяти часов до 8 часов",
    "более 8 часов"
]
screen_time_ids = ["1", "2", "3", "4", "5"]

focus_options = [
    "Совсем не сфокусирован(а). Постоянно отвлекаюсь на мелочи.",
    "Скорее не сфокусирован(а). Важные задачи часто откладываю.",
    "Иногда да, иногда нет. Есть пространство для улучшений.",
    "В основном да. Стараюсь придерживаться приоритетов.",
    "Абсолютно сфокусирован(а). Целенаправленно движусь к главным целям."
]
focus_ids = ["1", "2", "3", "4", "5"]

changes_options = [
    "Кардинально (полный пересмотр привычек, чувствую себя по-другому)",
    "Значительно (сократил(а) время, стал(а) осознаннее, есть явный прогресс)",
    "Умеренно (некоторые привычки изменились, но есть над чем работать)",
    "Слегка (отдельные небольшие улучшения, но в целом все как раньше)",
    "Не изменились (не заметил(а) никакой разницы)",
]
changes_ids = ["1", "2", "3", "4", "5"]

useful_options = [
    "Да, очень полезно",
    "Да, но есть что улучшить",
    "Скорее да, чем нет",
    "Затрудняюсь ответить",
    "Скорее нет, чем да",
    "Нет, совершенно бесполезно"
]
useful_ids = ["1", "2", "3", "4", "5", "6"]

def get_time_keyboard():
    builder = InlineKeyboardBuilder()
    for time, time_id in zip(times, time_ids):
        builder.button(text=time, callback_data=f"time_{time_id}")
    builder.adjust(4)
    return builder.as_markup()

def get_screen_time_keyboard():
    builder = InlineKeyboardBuilder()
    for option, option_id in zip(screen_time_options, screen_time_ids):
        builder.button(text=option, callback_data=f"screen_{option_id}")
    builder.adjust(2)
    return builder.as_markup()

def get_focuses_keyboard():
    builder = InlineKeyboardBuilder()
    for option, option_id in zip(focus_options, focus_ids):
        builder.button(text=option, callback_data=f"focus_{option_id}")
    builder.adjust(1)
    return builder.as_markup()

def get_changes_keyboard():
    builder = InlineKeyboardBuilder()
    for option, option_id in zip(changes_options, changes_ids):
        builder.button(text=option, callback_data=f"change_{option_id}")
    builder.adjust(1)
    return builder.as_markup()

def get_useful_keyboard():
    builder = InlineKeyboardBuilder()
    for option, option_id in zip(useful_options, useful_ids):
        builder.button(text=option, callback_data=f"useful_{option_id}")
    builder.adjust(1)
    return builder.as_markup()

# Создаем фильтры для обработки callback_data
time = ["time_8", "time_10", "time_12", "time_18"]
screen_time = ["screen_1", "screen_2", "screen_3", "screen_4", "screen_5"]
focuses = ["focus_1", "focus_2", "focus_3", "focus_4", "focus_5"]
changes = ["change_1", "change_2", "change_3", "change_4", "change_5"]
useful = ["useful_1", "useful_2", "useful_3", "useful_4", "useful_5", "useful_6"]



def get_text_by_id(data_id, options, ids):
    """Получить текст опции по ID"""
    try:
        index = ids.index(data_id.split('_')[-1])
        return options[index]
    except (ValueError, IndexError):
        return "Неизвестный вариант"