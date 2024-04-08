from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from .text_on_kb import back_to_global_answers


# --- Кнопки под клавиатурой для возвращения в ленту ответов --- #
def back_to_answers_kb() -> ReplyKeyboardMarkup:
    kb = [[KeyboardButton(text=back_to_global_answers)]]
    return ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True
    )
