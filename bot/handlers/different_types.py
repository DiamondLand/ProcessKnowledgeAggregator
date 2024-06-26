import random

from aiogram import Router, F
from aiogram.types import Message

router = Router()


thank_you_sticker_messages = [
    "Стикеры - это круто. Лайк тебе 👍",
    "Милый стикер. Лайк тебе 👍",
    "Неплохо, неплохо 😎",
    "Сохраню, пожалуй, себе этот стикер. Не против 😉?",
    "Стикеры стикерами, а просмотр вопросов по расписанию!",
    "Я люблю стикеры, но давай лучше найдём ответ на вопрос? 😉",
    "Стикер... Но вопросы не ждут! Давай посмотрим их 🐣!",
    "А у тебя есть ещё один 🥺?",
    "КРАСОТЕНЬ ТО КАКАЯ!"
]

thank_you_animation_messages = [
    "Гифки - это круто. Лайк тебе 👍",
    "Милая гифка. Лайк тебе 👍",
    "Неплохо, неплохо 😎",
    "Сохраню, пожалуй, себе эту гифку. Не против 😉?",
    "Гифка гифками, а просмотр вопросов по расписанию!",
    "Я люблю гифками, но давай лучше ответ на вопрос? 😉",
    "Гифка... Но вопросы не ждут! Давай посмотрим их 🐣!",
    "А у тебя есть ещё одна 🥺?",
    "КРАСОТЕНЬ ТО КАКАЯ!"
]


@router.message(F.sticker)
async def message_with_sticker(message: Message):
    await message.answer(text=random.choice(thank_you_sticker_messages))

@router.message(F.animation)
async def message_with_gif(message: Message):
    await message.answer(text=random.choice(thank_you_animation_messages))

@router.message(F.text)
async def message_with_text(message: Message):
    await message.answer(text="Нет такого варианта!")