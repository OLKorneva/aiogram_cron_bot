from aiogram.utils.keyboard import InlineKeyboardBuilder

screen_time_options = [
    "менее часа",
    "от часа до двух",
    "от двух часов до пяти",
    "от пяти часов до 8 часов",
    "более 8 часов"
]
screen_time_ids = ["1", "2", "3", "4", "5"]

focus_options = [
    "🚫 Совсем не сфокусирован(а)",
    "⚠️ Скорее не сфокусирован(а)",
    "🔁 Иногда сфокусирован, иногда нет",
    "✅ В основном сфокусирован(а)",
    "🎯 Полностью сфокусирован(а)"
]
focus_ids = ["1", "2", "3", "4", "5"]

changes_options = [
    "🙌 Меньше завишу от телефона",
    "📝 Работаю более сфокусированно",
    "👨‍👩‍👧‍ Более качественно провожу время с семьей и друзьями",
    "🛏 Не беру телефон в спальню",
    "⭐ Все вышеперечисленное"
]
changes_ids = ["1", "2", "3", "4", "5"]

useful_options = [
    "✅ Очень полезно",
    "👍 Полезно",
    "🤔 Скорее да",
    "😐 Затрудняюсь",
    "👎 Скорее нет",
    "❌ Бесполезно"
]
useful_ids = ["1", "2", "3", "4", "5", "6"]


feedback_options = [
    "👍 Нравятся",
    "👎 Скорее не нравятся",
    "🤷 Не знаю"
]
feedback_ids = ["1", "2", "3"]

else_challenge_options = [
    "👍 Да!",
    "👎 Скорее нет"
]
else_challenge_ids = ["1", "2"]


def get_screen_time_keyboard():
    builder = InlineKeyboardBuilder()
    for option, option_id in zip(screen_time_options, screen_time_ids):
        builder.button(text=option, callback_data=f"screen_{option_id}")
    builder.adjust(1)
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

def get_else_challenge_keyboard():
    builder = InlineKeyboardBuilder()
    for option, option_id in zip(else_challenge_options, else_challenge_ids):
        builder.button(text=option, callback_data=f"else_{option_id}")
    builder.adjust(2)
    return builder.as_markup()

def get_feedback():
    builder = InlineKeyboardBuilder()
    for option, option_id in zip(feedback_options, feedback_ids):
        builder.button(text=option, callback_data=f"feedback_{option_id}")
    builder.adjust(1)
    return builder.as_markup()

# Создаем фильтры для обработки callback_data
time = ["time_8", "time_10", "time_12", "time_18"]
screen_time = ["screen_1", "screen_2", "screen_3", "screen_4", "screen_5"]
focuses = ["focus_1", "focus_2", "focus_3", "focus_4", "focus_5"]
changes = ["change_1", "change_2", "change_3", "change_4", "change_5"]
useful = ["useful_1", "useful_2", "useful_3", "useful_4", "useful_5", "useful_6"]
else_challenge = ["else_1", "else_2"]
feedback = ["feedback_1", "feedback_2", "feedback_3"]

def get_text_by_id(data_id, options, ids):
    """Получить текст опции по ID"""
    try:
        index = ids.index(data_id.split('_')[-1])
        return options[index]
    except (ValueError, IndexError):
        return "Неизвестный вариант"