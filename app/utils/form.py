from aiogram.fsm.state import State, StatesGroup

# FSM для сбора ответов
class UserForm(StatesGroup):
    waiting_for_question_name = State()
    waiting_for_question_screen_time = State()
    waiting_for_question_focus = State()
    waiting_for_question_changes = State()

    waiting_for_feedback = State()

    waiting_for_after_screen_time = State()
    waiting_for_after_focus = State()
    waiting_for_after_changes = State()

    waiting_for_is_useful = State()
    waiting_for_whats_new = State()
    waiting_for_whats_changed = State()
    waiting_for_else_challenge = State()
    waiting_for_topics = State()

    # Новые состояния для дополнительных вопросов
    waiting_for_is_need = State()          # Нужен ли такой эксперимент?
    waiting_for_reflection_time = State()  # Время на осмысление
    waiting_for_is_watched = State()       # Смотрели ли статистику