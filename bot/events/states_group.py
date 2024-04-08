from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import StateFilter


# --- StatesGroup для регистрации аккаунта ---
class CreateProfile(StatesGroup):
    create_login = State()
    create_password = State()
    create_contacts = State()


# --- StatesGroup для авторизации аккаунта ---
class Authorizationrofile(StatesGroup):
    authorization_login = State()
    authorization_password = State()


# --- StatesGroup просмотра лент вопросов ---
class Searching(StatesGroup):
    tape_questions = State()
    tape_answers = State()

    view_answers = State()

    create_question = State()
    create_answer = State()


# --- StatesGroup изменения вопросов/ответов  ---
class EditQuestionOrAnswer(StatesGroup):
    edit_question = State()
    edit_question_tag = State()
    edit_answer = State()


# --- StatesGroup для ввода каптчи ---
class Captcha(StatesGroup):
    captcha_input = State()
