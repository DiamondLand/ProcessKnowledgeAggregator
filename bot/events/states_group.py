from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import StateFilter


# --- StatesGroup для регистрации аккаунта ---
class CreateProfile(StatesGroup):
    create_login = State()
    create_password = State()
    create_contacts = State()


# --- StatesGroup для добавления в чёрный список ---
class AddRemoveBlacklist(StatesGroup):
    blacklist_login_to_add = State()
    blacklist_login_to_remove = State()
    blacklist_reason = State()


# --- StatesGroup для авторизации аккаунта ---
class Authorizationrofile(StatesGroup):
    authorization_login = State()
    authorization_password = State()


# --- StatesGroup просмотра лент вопросов ---
class Searching(StatesGroup):
    tape_questions = State()
    tape_tag_questions_write = State()
    tape_tag_questions = State()
    tape_answers = State()


# --- StatesGroup Создание вопроса ---
class CreateQuestion(StatesGroup):
    create_question = State()
    create_question_tag = State()
    create_question_photo = State()


# --- StatesGroup Создание ответа ---
class CreateAnswer(StatesGroup):
    create_answer = State()
    create_answer_photo = State()


# --- StatesGroup изменения вопросов/ответов  ---
class EditQuestionOrAnswer(StatesGroup):
    edit_question = State()
    edit_question_tag = State()
    edit_answer = State()


# --- StatesGroup для ввода каптчи ---
class Captcha(StatesGroup):
    captcha_input = State()
