from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from .text_on_kb import (next_question, vote_question, answer_question, edit_my_question,
                         view_answers_my_question, view_answers_question, next_my_question, answer_my_question, back,
                         next_my_answer, next_all_answer, vote_answer, edit_my_answer)


# --- Панель просмотра всех вопросов ---
def all_questions_kb() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text=view_answers_question), KeyboardButton(text=next_question)],
        [KeyboardButton(text=answer_question)],
        [KeyboardButton(text=vote_question)],
        [KeyboardButton(text=back)]
    ]
    return ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Все вопросы"
    )


# --- Панель просмотра собственных вопросов ---
def my_questions_kb() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text=view_answers_my_question), KeyboardButton(text=next_my_question)],
        [KeyboardButton(text=answer_my_question)],
        [KeyboardButton(text=edit_my_question)],
        [KeyboardButton(text=back)]
    ]
    return ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Собственные вопросы"
    )


# --- Панель просмотра всех ответов ---
def all_answers_kb() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text=next_all_answer), KeyboardButton(text=vote_answer)],
        [KeyboardButton(text=back)]
    ]
    return ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Все ответы"
    )


# --- Панель просмотра всех ответов ---
def my_answers_kb() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text=next_my_answer), KeyboardButton(text=edit_my_answer)],
        [KeyboardButton(text=back)]
    ]
    return ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Собственные ответы"
    )
