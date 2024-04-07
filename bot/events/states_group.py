from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import StateFilter


# --- StatesGroup для регистрации аккаунта ---
class CreateProfile(StatesGroup):
    create_login = State()
    create_password = State()
    create_contacts = State()


# --- StatesGroup для ввода каптчи ---
class Captcha(StatesGroup):
    captcha_input = State()