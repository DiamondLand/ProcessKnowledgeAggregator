from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from .text_on_kb import recreate_profile, reg_profile, auth_profile, my_questions, my_answers, my_statistic


# --- Кнопки под клавиатурой для взаимодействия с профилем --- #
def profile_kb() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text=auth_profile)],
        [KeyboardButton(text=my_questions), KeyboardButton(text=my_answers)],
        [KeyboardButton(text=my_statistic)]
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