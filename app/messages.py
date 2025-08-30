from os import getenv
from dotenv import load_dotenv

load_dotenv()

URL_MEETING_1 = "https://youandpartners.ru/"
URL_MEETING_2 = "https://youandpartners.ru/"
URL_MEETING_3 = "https://youandpartners.ru/"
CHANNEL_ID = getenv("SOURCE_CHAT_ID")


dialogue_messages = {
    'start': {'forward_key': 15},
    'chose_time': {'forward_key': 16},
    'confirm_time': {'forward_key': 17},
    'final_questions_start': {'forward_key': 46},
    'thanks': {'forward_key': 47}
}

questions = {
    'name': 'Пожалуйста, напиши свое имя:',
    'screen_time': 'Сколько времени ты проводишь у экрана телефона ежедневно?',
    'focus': 'Насколько ты сфокусирован(а) на себе и на важном?',
    'changes': 'Что бы ты хотел изменить?',
    'feedback': '{}, прошли 7 дней челленджа. Поделись, пожалуйста, своими впечатлениями, насколько тебе нравятся челлендж и задания?',
    'final_questions': '''Привет, {}! 
    
✨ Помнишь, в начале челленджа я задавал тебе вопросы? Давай вспомним эти вопросы и ответы на них!''',
    'after_screen_time': 'Сколько времени ты теперь проводишь у экрана телефона ежедневно?',
    'after_focus': 'Насколько теперь ты сфокусирован(а) на себе и на важном?',
    'is_useful': 'Было ли для тебя полезным участие в челлендже?',
    'whats_new': 'Что нового ты для себя открыл(а)?',
    'whats_changed': 'Как поменялись твои цифровые привычки?',
    'else_challenge': 'Хотел бы ты принять участие в других челленджах?',
    'topics': 'Напиши, пожалуйста, какие темы челленджей тебе были бы интересны:'
}

confirms = {
    'name': 'Приятно познакомиться, {}! Меня зовут Фокус. 🐾',
    'screen_time': 'Хорошо, твое 🕐 экранное время сейчас: <b>{}</b>',
    'focus': 'Твой фокус сейчас: <b>{}</b>',
    'save_first_result': '''✨ <b>{}, cовсем скоро мы начнем наш челлендж!</b>  ✨

✅ Я зафиксировал твои ожидания от челленджа. По его окончании проверим, что удалось совместно сделать! 

#вернисвойфокус''',
    'feedback': 'Спасибо за отзыв!',
    'after_screen_time': 'До челленджа твое экранное время было: <b>{}</b>, сейчас: <b>{}</b>!',
    'after_focus': '''До челледжа ты сообщил(а) мне о своем фокусе следующее: <b>{}</b>, сейчас: <b>{}</b>.''',
    'useful': 'Спасибо! Твое мнение важно для меня! 🐾',
    'changed': 'Спасибо за твой ответ!🤝',
    'after_changed': 'До челледжа ты хотел(а) изменить: <b>{}</b>. Подумай, получилось ли достичь своей цели? Рад, если помог тебе!',
    'save_final_result': '''✨ Спасибо тебе, что эти две недели мы провели вместе. Мне было приятно с тобой общаться и узнавать о тебе новое! 

Твой бот Фокус 🐾'''
}


timetable_single_messages =[
    {
        "time": {"year":"2025", "month":"08", "day":"29", "hour":"17", "minute":"13"},
        "message_key": "first_meeting_invite",
        'forward_key': 100
    },
    {
        "time": {"year":"2025", "month":"08", "day":"29", "hour":"17", "minute":"14"},
        "message_key": "first_meeting_1_remind",
        'forward_key': 102
    },
    {
        "time": {"year":"2025", "month":"08", "day":"29", "hour":"17", "minute":"15"},
        "message_key": "first_meeting_2_remind",
        'forward_key': 103
    },
    {
        "time": {"year":"2025", "month":"08", "day":"29", "hour":"17", "minute":"16"},
        "message_key": "first_meeting_record",
        'forward_key': 104
    },
    {
        "time": {"year":"2025", "month":"08", "day":"29", "hour":"17", "minute":"17"},
        "message_key": "content",
        'forward_key': 105
    },
    {
        "time": {"year":"2025", "month":"08", "day":"29", "hour":"17", "minute":"18"},
        "message_key": "middle_meeting_invite",
        'forward_key': 106
    },
    {
        "time": {"year":"2025", "month":"08", "day":"29", "hour":"17", "minute":"19"},
        "message_key": "middle_meeting_record",
        'forward_key': 107
    },
    {
        "time": {"year":"2025", "month":"08", "day":"29", "hour":"17", "minute":"20"},
        "message_key": "final_meeting_invite",
        'forward_key': 109
    },
    {
        "time": {"year":"2025", "month":"08", "day":"29", "hour":"17", "minute":"21"},
        "message_key": "feedback",
    },
    {
        "time": {"year":"2025", "month":"08", "day":"29", "hour":"17", "minute":"22"},
        "message_key": "final",
        'forward_key': 113
    }
]