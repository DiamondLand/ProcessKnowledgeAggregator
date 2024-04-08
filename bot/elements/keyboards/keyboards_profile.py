from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from .text_on_kb import recreate_profile, reg_profile, auth_profile


# --- Кнопки под клавиатурой для взаимодействия с профилем --- #
def profile_kb() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text=recreate_profile)],
        [KeyboardButton(text=reg_profile)],
        [KeyboardButton(text=auth_profile)]
    ]
    return ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True
    )


# --- Кнопка под клавиатурой для пересоздания профиля --- #
def recreate_profile_kb() -> ReplyKeyboardMarkup:
    kb = [[KeyboardButton(text=recreate_profile)]]
    return ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True
    )


# --- Кнопки под клавиатурой для регистрации/авторизации профиля --- #
def reg_or_auth_kb() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text=reg_profile)],
        [KeyboardButton(text=auth_profile)]
    ]
    return ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True
    )