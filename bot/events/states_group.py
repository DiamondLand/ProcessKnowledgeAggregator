from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import StateFilter


# --- StatesGroup для ввода каптчи ---
class Captcha(StatesGroup):
    captcha_input = State()