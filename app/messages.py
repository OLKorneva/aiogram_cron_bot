from os import getenv
from dotenv import load_dotenv

load_dotenv()
CHANNEL_ID = getenv("SOURCE_CHAT_ID")


dialogue_messages = {
    'start': {'forward_key': 40}
}

questions = {
    'name': 'Пожалуйста, напиши свое имя:',
    'screen_time': 'Сколько времени ты проводишь у экрана телефона ежедневно?',
    'focus': 'Насколько ты сфокусирован(а) на себе и на важном?',
    'changes': 'Что бы ты хотел изменить?',
    'feedback': '{}, прошли 10 дней челленджа. Поделись, пожалуйста, своими впечатлениями, насколько тебе нравятся челлендж и задания?',
    'final_questions': '''Привет, {}! 
    
✨ Помнишь, в начале челленджа я задавал тебе вопросы? Давай вспомним эти вопросы и ответы на них!''',
    'after_screen_time': 'Сколько времени ты теперь проводишь у экрана телефона ежедневно?',
    'after_focus': 'Насколько теперь ты сфокусирован(а) на себе и на важном?',
    'is_useful': 'Было ли для тебя полезным участие в челлендже?',
    'whats_new': 'Что нового ты для себя открыл(а)?',
    'whats_changed': 'Как поменялись твои цифровые привычки?',
    'else_challenge': 'Хотел бы ты принять участие в других челленджах?',
    'topics': 'Напиши, пожалуйста, какие темы челленджей тебе были бы интересны:',
    'is_need': 'И теперь еще пара вопросов. Нужны ли тебе рефлексии?',
    'reflection_time': 'Оптимальное время для рефлексий?',
    'is_watched': 'Смотрел ли ты рефлексии в записи?',
}

confirms = {
    'name': '<em>Приятно познакомиться, {}! Меня зовут Фокус. 🐾</em>',
    'screen_time': '<em>Хорошо, твое 🕐 экранное время сейчас: <b>{}</b></em>',
    'focus': '<em>Твой фокус сейчас: <b>{}</b></em>',
    'save_first_result': '''<em>✨ <b>{}, cовсем скоро мы начнем наш челлендж!</b>  ✨

✅ Я зафиксировал твои ожидания от челленджа. По его окончании проверим, что удалось совместно сделать! </em>

#вернисвойфокус''',
    'feedback': '<em>Спасибо за отзыв!</em>',
    'after_screen_time': '<em>До челленджа твое экранное время было: <b>{}</b>, сейчас: <b>{}</b>!</em>',
    'after_focus': '''<em>До челледжа ты сообщил(а) мне о своем фокусе следующее: <b>{}</b>, сейчас: <b>{}</b>.</em>''',
    'useful': '<em>Спасибо! Твое мнение важно для меня! 🐾</em>',
    'changed': '<em>Спасибо за твой ответ!🤝</em>',
    'after_changed': '<em>До челледжа ты хотел(а) изменить: <b>{}</b>. Подумай, получилось ли достичь своей цели? Рад, если помог тебе!</em>',
    'is_need': '<em>Спасибо!</em>',
    'reflection_time': '<em>Отлично, оптимальное время рефлексии: <b>{}</b></em>',
    'is_watched': '<em>Спасибо за ответ!</em>',
    'save_final_result': '''<em>✨ Спасибо тебе, что эти две недели мы провели вместе. Мне было приятно с тобой общаться и узнавать о тебе новое! 

Твой бот Фокус 🐾</em>'''
}


timetable_single_messages =[
    {
        "time": {"year":"2025", "month":"09", "day":"05", "hour":"15", "minute":"00"},
        "message_key": "first_meeting_invite",
        'forward_key': 5
    },
    {
        "time": {"year":"2025", "month":"09", "day":"06", "hour":"10", "minute":"00"},
        "message_key": "first_meeting_1_remind",
        'forward_key': 6
    },
    {
        "time": {"year":"2025", "month":"09", "day":"06", "hour":"11", "minute":"45"},
        "message_key": "first_meeting_2_remind",
        'forward_key': 7
    },
    {
        "time": {"year":"2025", "month":"09", "day":"06", "hour":"19", "minute":"45"},
        "message_key": "first_meeting_record",
        'forward_key': 8
    },
    {
        "time": {"year":"2025", "month":"09", "day":"05", "hour":"10", "minute":"10"},
        "message_key": "content",
        'forward_key': 9
    },
    {
        "time": {"year":"2025", "month":"09", "day":"12", "hour":"15", "minute":"00"},
        "message_key": "middle_meeting_invite",
        'forward_key': 11
    },
    {
        "time": {"year":"2025", "month":"09", "day":"13", "hour":"10", "minute":"00"},
        "message_key": "middle_meeting_1_remind",
        'forward_key': 12
    },
    {
        "time": {"year":"2025", "month":"09", "day":"13", "hour":"11", "minute":"45"},
        "message_key": "middle_meeting_2_remind",
        'forward_key': 13
    },
    {
        "time": {"year":"2025", "month":"09", "day":"14", "hour":"15", "minute":"00"},
        "message_key": "middle_meeting_record",
        'forward_key': 14
    },
    {
        "time": {"year":"2025", "month":"09", "day":"20", "hour":"15", "minute":"00"},
        "message_key": "final_meeting_invite",
        'forward_key': 18
    },
    {
        "time": {"year":"2025", "month":"09", "day":"21", "hour":"10", "minute":"00"},
        "message_key": "final_meeting_1_remind",
        'forward_key': 19
    },
    {
        "time": {"year":"2025", "month":"09", "day":"21", "hour":"11", "minute":"45"},
        "message_key": "final_meeting_2_remind",
        'forward_key': 20
    },
    {
        "time": {"year":"2025", "month":"09", "day":"22", "hour":"15", "minute":"00"},
        "message_key": "final_record",
        'forward_key': 21
    },
    {
        "time": {"year":"2025", "month":"09", "day":"16", "hour":"12", "minute":"00"},
        "message_key": "feedback",
    },
    {
        "time": {"year":"2025", "month":"09", "day":"22", "hour":"18", "minute":"00"},
        "message_key": "final",
    }
]

# timetable_single_messages =[
#     {
#         "time": {"year":"2025", "month":"09", "day":"03", "hour":"11", "minute":"00"},
#         "message_key": "first_meeting_invite",
#         'forward_key': 5
#     },
#     {
#         "time": {"year":"2025", "month":"09", "day":"03", "hour":"11", "minute":"05"},
#         "message_key": "first_meeting_1_remind",
#         'forward_key': 6
#     },
#     {
#         "time": {"year":"2025", "month":"09", "day":"03", "hour":"11", "minute":"10"},
#         "message_key": "first_meeting_2_remind",
#         'forward_key': 7
#     },
#     {
#         "time": {"year":"2025", "month":"09", "day":"03", "hour":"11", "minute":"15"},
#         "message_key": "first_meeting_record",
#         'forward_key': 8
#     },
#     {
#         "time": {"year":"2025", "month":"09", "day":"03", "hour":"11", "minute":"20"},
#         "message_key": "content",
#         'forward_key': 9
#     },
#     {
#         "time": {"year":"2025", "month":"09", "day":"03", "hour":"11", "minute":"25"},
#         "message_key": "middle_meeting_invite",
#         'forward_key': 11
#     },
#     {
#         "time": {"year":"2025", "month":"09", "day":"03", "hour":"11", "minute":"35"},
#         "message_key": "middle_meeting_1_remind",
#         'forward_key': 12
#     },
#     {
#         "time": {"year":"2025", "month":"09", "day":"03", "hour":"11", "minute":"40"},
#         "message_key": "middle_meeting_2_remind",
#         'forward_key': 13
#     },
#     {
#         "time": {"year":"2025", "month":"09", "day":"03", "hour":"11", "minute":"45"},
#         "message_key": "middle_meeting_record",
#         'forward_key': 14
#     },
#     {
#         "time": {"year":"2025", "month":"09", "day":"03", "hour":"11", "minute":"50"},
#         "message_key": "final_meeting_invite",
#         'forward_key': 18
#     },
#     {
#         "time": {"year":"2025", "month":"09", "day":"03", "hour":"11", "minute":"55"},
#         "message_key": "final_meeting_1_remind",
#         'forward_key': 19
#     },
#     {
#         "time": {"year":"2025", "month":"09", "day":"03", "hour":"12", "minute":"00"},
#         "message_key": "final_meeting_2_remind",
#         'forward_key': 20
#     },
#     {
#         "time": {"year":"2025", "month":"09", "day":"03", "hour":"12", "minute":"05"},
#         "message_key": "final_record",
#         'forward_key': 21
#     },
#     {
#         "time": {"year":"2025", "month":"09", "day":"03", "hour":"11", "minute":"30"},
#         "message_key": "feedback",
#     },
#     {
#         "time": {"year":"2025", "month":"09", "day":"03", "hour":"12", "minute":"10"},
#         "message_key": "final",
#     }
# ]