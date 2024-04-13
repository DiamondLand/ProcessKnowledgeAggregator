import random
import string

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from .text_on_kb import cancel_button


# --- Кнопка под клавиатурой для отмены заполнения формы --- #
def form_cancel_kb() -> ReplyKeyboardMarkup:
    kb = [[KeyboardButton(text=cancel_button)]]
    return ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True
    )


# --- Кнопка под клавиатурой для генерации пароля --- #
def generate_password_kb() -> ReplyKeyboardMarkup:
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=7))
    kb = [
        [KeyboardButton(text=password)],
        [KeyboardButton(text=cancel_button)]
    ]
    return ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True
    )