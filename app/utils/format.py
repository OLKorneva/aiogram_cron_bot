from datetime import datetime, timedelta
import math

month_names = {
        "January": "января",
        "February": "февраля",
        "March": "марта",
        "April": "апреля",
        "May": "мая",
        "June": "июня",
        "July": "июля",
        "August": "августа",
        "September": "сентября",
        "October": "октября",
        "November": "ноября",
        "December": "декабря"
    }

month_numbers = {
        '01': "января",
        '02': "февраля",
        '03': "марта",
        '04': "апреля",
        '05': "мая",
        '06': "июня",
        '07': "июля",
        '08': "августа",
        '09': "сентября",
        '10': "октября",
        '11': "ноября",
        '12': "декабря"
    }

# Функция для получения завтрашней даты в формате "6 сентября"
def get_tomorrow_day():
    tomorrow = datetime.today() + timedelta(days=1)
    return f"{tomorrow.day} {month_names[tomorrow.strftime('%B')]}"

# Функция для получения даты в формате "6 сентября" из формата "2025-09-06"
def get_formated_day(date: str) -> str | None:
    if not isinstance(date, str):
        return None
    _, month, day = date.split('-')
    month = month_numbers.get(month, None)
    if month and 1 <= int(day) <= 31:
        return day.lstrip('0') + ' ' + month
    return None



def format_text_to_width(text, width_px):
    """Форматирует текст с сохранением пустых строк и переносов"""
    # Рассчитываем примерное количество символов в строке
    chars_per_line = max(40, math.floor(width_px / 15))  # Не менее 40 символов

    result = []
    for paragraph in text.split('\n'):
        if not paragraph.strip():  # Сохраняем пустые строки
            result.append('')
            continue

        words = paragraph.split()
        current_line = []

        for word in words:
            # Проверяем, помещается ли слово в текущую строку
            line_length = sum(len(w) for w in current_line) + len(current_line)  # + пробелы
            if line_length + len(word) <= chars_per_line:
                current_line.append(word)
            else:
                result.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            result.append(' '.join(current_line))

    return '\n'.join(result)

