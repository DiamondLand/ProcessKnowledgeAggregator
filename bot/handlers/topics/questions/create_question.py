import httpx
import re

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from decorators.profile_decorator import check_authorized

from elements.keyboards.keyboards_profile import profile_kb
from elements.keyboards.text_on_kb import create_question

from elements.keyboards.keyboards_utilits import form_cancel_kb
from elements.keyboards.keyboards_questions import tags_to_question_kb

from elements.answers import no_state, server_error

from events.states_group import CreateQuestion

router = Router()


# --- Задать вопрос --- #
@router.message(F.text == create_question)
async def create_question_handler(message: Message, state: FSMContext):
    # Если стадия существует, выходим из неё
    current_state = await state.get_state()
    if current_state is not None:
        await state.clear()

    await state.set_state(CreateQuestion.create_question)

    await message.answer(
        text=f"Какой у вас вопрос? Введите его в чат:",
        reply_markup=form_cancel_kb()
    )


# --- Отправка вопроса -> выбор тега --- #
@router.message(CreateQuestion.create_question)
async def create_question_choice(message: Message, state: FSMContext):
    # Если стадия существует, выходим из неё
    current_state = await state.get_state()
    if current_state is not None and current_state != CreateQuestion.create_question:
        await state.clear()

    cleaned_text = re.sub(r'[<>]', '', message.text.capitalize())  # Убираем символы выделения
    if len(cleaned_text) < 4 or len(cleaned_text) > 1000:
        return await message.answer(text="❌ Текст должен быть не короче 4 и не длиннее 1.000 символов! Пожалуйста, повторите ввод:")

    data = await state.get_data()
    data['question'] = cleaned_text
    await state.update_data(data)

    await state.set_state(CreateQuestion.create_question_tag)

    await message.answer(
        text=f"Какая категория у вопроса? Введите тег или выберите самые популярные по кнопкам ниже:",
        reply_markup=await tags_to_question_kb(config=message.bot.config)
    )


# --- Выбор тега -> финищ --- #
@router.message(CreateQuestion.create_question_tag)
@check_authorized
async def create_question_tag_choice(message: Message, state: FSMContext, get_user_response: dict):
    data = await state.get_data()

    # Проверка на существование формы для заполнения
    if not data:
        await state.clear()
        return await message.answer(text=no_state, reply_markup=profile_kb())

    cleaned_text = re.sub(r'[<>]', '', message.text.capitalize())  # Убираем символы выделения
    if len(cleaned_text) < 4 or len(cleaned_text) > 1000:
        return await message.answer(text="❌ Текст должен быть не короче 4 и не длиннее 1.000 символов! Пожалуйста, повторите ввод:")

    async with httpx.AsyncClient() as client:
        create_answer_response = await client.post(message.bot.config['SETTINGS']['backend_url'] + 'create_question', json={
            "login": get_user_response['login'],
            "question": data.get('question', None),
            "tag": cleaned_text
        })

    if create_answer_response.status_code == 200:
        await state.clear()

        await message.answer(
            text="💛 Вопрос задан! Подождём ответов!",
            reply_markup=profile_kb()
        )
    else:
        await message.answer(text=server_error)