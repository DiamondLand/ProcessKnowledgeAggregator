from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


# --- Кнопка завершения регистрации --- #
def finish_registration_btns() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="Завершить ✨",
            callback_data="finish_registration"
        )
    )
    return builder


# --- Кнопка завершения создания вопроса --- #
def finish_questions_btns() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="Завершить ✨",
            callback_data="finish_questions"
        )
    )
    return builder


# --- Кнопка завершения создания ответов --- #
def finish_answers_btns() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="Завершить ✨",
            callback_data="finish_answers"
        )
    )
    return builder
