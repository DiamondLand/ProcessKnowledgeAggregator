from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from .text_on_kb import back_to_global_questions, back_to_my_questions


# --- Кнопки под клавиатурой для возвращения в ленту всех вопросов --- #
def back_to_global_questions_kb() -> ReplyKeyboardMarkup:
    kb = [[KeyboardButton(text=back_to_global_questions)]]
    return ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True
    )


# --- Кнопки под клавиатурой для возвращения в ленту собственных вопросов --- #
def back_to_my_questions_kb() -> ReplyKeyboardMarkup:
    kb = [[KeyboardButton(text=back_to_my_questions)]]
    return ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True
    )
