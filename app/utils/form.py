from aiogram.fsm.state import State, StatesGroup

# FSM для сбора ответов
class UserForm(StatesGroup):
    waiting_for_question_name = State()
    waiting_for_question_screen_time = State()
    waiting_for_question_focus = State()
    waiting_for_question_changes = State()
    waiting_for_time = State()

    waiting_for_after_screen_time = State()
    waiting_for_after_focus = State()
    waiting_for_after_changes = State()

    waiting_for_is_useful = State()
    waiting_for_whats_new = State()
    waiting_for_whats_changed = State()