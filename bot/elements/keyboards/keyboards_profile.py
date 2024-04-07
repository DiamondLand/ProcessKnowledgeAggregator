from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from .text_on_kb import recreate_profile


# --- Кнопка под клавиатурой для пересоздания профиля --- #
def recreate_profile_kb() -> ReplyKeyboardMarkup:
    kb = [[KeyboardButton(text=recreate_profile)]]
    return ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True
    )