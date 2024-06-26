from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


# --- Кнопка завершения регистрации --- #
def admins_btns() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text="Модерация вопросов",
            callback_data="moder_questions"
        ),
        InlineKeyboardButton(
            text="Модерация ответов",
            callback_data="moder_answers"
        ),
        InlineKeyboardButton(
            text="Чёрный список",
            callback_data="get_blacklist"
        ),
        InlineKeyboardButton(
            text="В чёрный список",
            callback_data="add_to_blacklist"
        ),
        InlineKeyboardButton(
            text="Из чёрного списка",
            callback_data="remove_from_blacklist"
        ),
        InlineKeyboardButton(
            text="Запустить рассылку",
            callback_data="mailing"
        ),
        InlineKeyboardButton(
            text="Написать по логину в ЛС",
            callback_data="send_dm"
        ),
        InlineKeyboardButton(
            text="Удалить аккаунт по логину",
            callback_data="delete_login"
        )
    )
    builder.adjust(2, 1)
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
