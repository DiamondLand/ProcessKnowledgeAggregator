from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from .text_on_kb import cancel_button


# --- Кнопка под клавиатурой для отмены заполнения формы --- #
def form_cancel_kb() -> ReplyKeyboardMarkup:
    kb = [[KeyboardButton(text=cancel_button)]]
    return ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True
    )
