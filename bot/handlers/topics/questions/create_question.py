import httpx
import random
import string
import re

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from decorators.profile_decorator import check_authorized

from functions.views_logic.looped_tape import send_searching_questions
from functions.inline_remove import remove_button

from elements.keyboards.keyboards_searching import my_questions_kb
from elements.keyboards.keyboards_profile import profile_kb
from elements.keyboards.text_on_kb import create_question

from elements.inline.inline_profile import finish_questions_btns
from elements.keyboards.keyboards_utilits import form_cancel_kb
from elements.keyboards.keyboards_questions import tags_to_question_kb

from elements.answers import no_state, server_error

from events.states_group import CreateQuestion, EditQuestionOrAnswer, Searching

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


# --- Выбор тега -> финиш --- #
@router.message(CreateQuestion.create_question_tag)
@check_authorized
async def create_question_tag_choice(message: Message, state: FSMContext, get_user_response: dict):
    data = await state.get_data()

    # Проверка на существование формы для заполнения
    if not data:
        await state.clear()
        return await message.answer(text=no_state, reply_markup=profile_kb())

    cleaned_text = re.sub(r'[<>]', '', message.text.capitalize())  # Убираем символы выделения
    if len(cleaned_text) < 4 or len(cleaned_text) > 100:
        return await message.answer(text="❌ Текст должен быть не короче 4 и не длиннее 100 символов! Пожалуйста, повторите ввод:")

    async with httpx.AsyncClient() as client:
        create_answer_response = await client.post(message.bot.config['SETTINGS']['backend_url'] + 'create_question', json={
            "login": get_user_response['login'],
            "question": data.get('question', None),
            "tag": cleaned_text
        })

    if create_answer_response.status_code == 200:
        await state.set_state(CreateQuestion.create_question_photo)

        data['question_id'] = create_answer_response.json()['id']
        data['user_response'] = get_user_response
        await state.update_data(data)

        await message.answer(
            text="🕐 Секундочку...",
            reply_markup=form_cancel_kb()
        )
        await message.answer(
            text="💛 Вопрос готов! Вы можете прикрепить к нему фотографию или опубликовать без неё:",
            reply_markup=finish_questions_btns().as_markup()
        )
    else:
        await message.answer(text=server_error)


# --- Отправка ответа к вопросу --- #
@router.message(CreateQuestion.create_question_photo)
async def create_question_photo(message: Message, state: FSMContext):
    # Если стадия существует, выходим из неё
    current_state = await state.get_state()
    if current_state is not None and current_state != CreateQuestion.create_question_photo:
        await state.clear()

    data = await state.get_data()

    # Проверка на существование формы для заполнения
    if not data:
        await state.clear()
        return await message.answer(text=no_state, reply_markup=profile_kb())

    if message.photo:
        question_id = data.get('question_id', None)
        get_user_response_json = data.get('user_response', None)

        letters = string.ascii_letters + string.digits

        file_path = f"bot/assets/questions/{question_id}_{get_user_response_json['login']}_{''.join(random.choice(letters) for _ in range(7))}.png"
        await message.bot.download(
            message.photo[-1],
            destination=file_path
        )

        await message.answer(
            text="💛 Вопрос готов! Вы можете отправить новую фотографию (для замены) или опубликовать!",
            reply_markup=finish_questions_btns().as_markup()
        )
    else:
        await message.answer(text="❌ Прикрепите фотографию или завершите заполение!")


# --- Финал --- #
@router.callback_query(F.data == "finish_questions")
async def finish_questions(callback: CallbackQuery, state: FSMContext):# -
    data = await state.get_data()

    # Удаляем кнопку с сообщения
    await remove_button(msg=callback.message, state=state)

    if not data:
        await state.clear()
        return await callback.message.answer(text=no_state)
    
    await state.clear()

    await callback.message.answer(
        text="💛 Вопрос задан и передан на модерацию! Мы уведомим вас о решении. Не выходите из аккаунта!",
        reply_markup=profile_kb()
    )


# === Редактирование вопроса ===


# --- Отправка вопроса -> выбор тега --- #
@router.message(EditQuestionOrAnswer.edit_question)
async def edit_question_choice(message: Message, state: FSMContext):
    data = await state.get_data()
    
    # Проверка на существование формы для заполнения
    if not data:
        await state.clear()
        return await message.answer(text=no_state, reply_markup=profile_kb())

    cleaned_text = re.sub(r'[<>]', '', message.text.capitalize())  # Убираем символы выделения

    if len(cleaned_text) < 4 or len(cleaned_text) > 1000:
        return await message.answer(text="❌ Текст должен быть не короче 4 и не длиннее 1.000 символов! Пожалуйста, повторите ввод:")

    data['new_question'] = cleaned_text
    await state.update_data(data)
    
    await message.answer(
        text=f"Какая категория у вопроса? Введите тег или выберите самые популярные по кнопкам ниже:",
        reply_markup=await tags_to_question_kb(config=message.bot.config)
    )

    await state.set_state(EditQuestionOrAnswer.edit_question_tag)


# --- Выбор тега -> финиш --- #
@router.message(EditQuestionOrAnswer.edit_question_tag)
async def edit_question_tag_choice(message: Message, state: FSMContext):
    data = await state.get_data()

    # Проверка на существование формы для заполнения
    if not data:
        await state.clear()
        return await message.answer(text=no_state, reply_markup=profile_kb())

    cleaned_text = re.sub(r'[<>]', '', message.text.capitalize())  # Убираем символы выделения
    if len(cleaned_text) < 4 or len(cleaned_text) > 100:
        return await message.answer(text="❌ Текст должен быть не короче 4 и не длиннее 100 символов! Пожалуйста, повторите ввод:")

    my_response = data.get('user_response', None)

    async with httpx.AsyncClient() as client:
        update_question_response = await client.put(message.bot.config['SETTINGS']['backend_url'] + 'update_question', json={
            "question_id": data.get("question_id", 1),
            "login": my_response['login'],
            "question": data.get('new_question', None),
            "tag": cleaned_text
        })

    if update_question_response.status_code == 200:
        await state.set_state(Searching.tape_questions)

        await message.answer(
            text="💛 Вопрос отредактирован и передан на модерацию!",
            reply_markup=my_questions_kb()
        )

        await send_searching_questions(
            message=message,
            state=state,
            my_response = my_response,
            set_index=False,
            global_tape=False
        )
    else:
        await message.answer(text=server_error)
