import httpx
import random

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from .text_on_kb import back_to_global_questions, back_to_my_questions, cancel_button, tag_general, tag_production, tag_salary, tag_workshops


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


# --- Кнопки под клавиатурой для тегов --- #
async def tags_to_question_kb(config) -> ReplyKeyboardMarkup:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{config['SETTINGS']['backend_url']}get_all_questions"
        )
    questions = response.json()[:5]

    if response.status_code == 200 and questions:
        buttons = []
        used_tags = set()

        for question in questions:
            tag = question.get('tag')
            if tag and tag not in used_tags:
                buttons.append([KeyboardButton(text=tag)])
                used_tags.add(tag)

        # Добавляем кнопки только если соответствующие теги еще не использованы
        if tag_general not in used_tags and tag_production not in used_tags:
            buttons.append([KeyboardButton(text=tag_general), KeyboardButton(text=tag_production)])
        if tag_salary not in used_tags and tag_workshops not in used_tags:
            buttons.append([KeyboardButton(text=tag_salary), KeyboardButton(text=tag_workshops)])

            buttons.append([KeyboardButton(text=cancel_button)])

            return ReplyKeyboardMarkup(
                keyboard=buttons,
                resize_keyboard=True
            )
    else:
        kb = [
            [KeyboardButton(text=tag_general) , KeyboardButton(text=tag_production)],
            [KeyboardButton(text=tag_salary), KeyboardButton(text=tag_workshops)],
            [KeyboardButton(text=cancel_button)],
        ]
        return ReplyKeyboardMarkup(
            keyboard=kb,
            resize_keyboard=True
        )
