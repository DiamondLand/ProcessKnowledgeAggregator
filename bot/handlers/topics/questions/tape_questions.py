import re

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from decorators.profile_decorator import check_authorized, anti_robot_check

from functions.views_logic.looped_tape import send_searching_questions

from elements.keyboards.keyboards_searching import my_questions_kb, all_questions_kb
from elements.keyboards.keyboards_questions import tags_to_question_kb
from elements.keyboards.keyboards_profile import profile_kb
from elements.keyboards.text_on_kb import (next_my_question, next_question, view_answers_my_question, view_answers_question, tag_searching,
                                           answer_my_question, answer_question, edit_my_question, vote_question, back_to_my_questions, back_to_global_questions,
                                           subscribe_my_question, subscribe_question)

from elements.answers import no_state

from events.states_group import Searching, EditQuestionOrAnswer

router = Router()


# --- Кнопки действий при просмотре ленты вопросов --- #
@router.message(
    Searching.tape_questions,
    (F.text == next_my_question) | (F.text == next_question) |
    (F.text == view_answers_my_question) | (F.text == view_answers_question) |
    (F.text == answer_my_question) | (F.text == answer_question) |
    (F.text == edit_my_question) | (F.text == vote_question) |
    (F.text == subscribe_my_question) | (F.text == subscribe_question)
)
@anti_robot_check
@check_authorized
async def questions_searching(message: Message, state: FSMContext, my_response: dict):
    # Если стадия существует, выходим из неё
    current_state = await state.get_state()
    if current_state is not None and current_state != Searching.tape_questions:
        await state.clear()

    actions = {
        'view_answers': message.text in [view_answers_my_question, view_answers_question],
        'edit': message.text in [edit_my_question],
        'vote': message.text in [vote_question],
        'create_answer': message.text in [answer_my_question, answer_question],
        'subscribe': message.text in [subscribe_my_question, subscribe_question],
        'global_tape': message.text in [
            next_question, view_answers_question, 
            answer_question, vote_question, subscribe_question
        ]
    }

    # Переходим в функцию просмотра ленты с дополнительными параметрами
    await send_searching_questions(
        message=message,
        state=state,
        my_response=my_response,
        **actions
    )


# --- Переход к вводу тега  --- #
@router.message( F.text == tag_searching)
async def tag_searching_func(message: Message, state: FSMContext):
    await message.answer(
        text="Введите тег, по которому хотите осуществить поиск или выберите из распространённых тегов, предложеных по кнопкам ниже:",
        reply_markup=await tags_to_question_kb(config=message.bot.config)
    )
    await state.set_state(Searching.tape_tag_questions_write)


# --- Отправка ответа к вопросу --- #
@router.message(Searching.tape_tag_questions_write)
@check_authorized
async def questions_tag_write(message: Message, state: FSMContext, my_response: dict):
    data = await state.get_data()

    cleaned_text = re.sub(r'[<>]', '', message.text.capitalize())  # Убираем символы выделения
    if len(cleaned_text) < 4 or len(cleaned_text) > 100:
        return await message.answer(text="❌ Текст должен быть не короче 4 и не длиннее 100 символов! Пожалуйста, повторите ввод:")

    data["tag"] = cleaned_text
    await state.update_data(data)

    await state.set_state(Searching.tape_tag_questions)
    
    # Отправялем эмодзи и задаём keyboard
    await message.answer(
        text=f"🔎 Просматривается лента по тегу <i>{cleaned_text}</i> ✨",
        reply_markup=all_questions_kb()
    )

    # Переходим в функцию просмотра ленты по тегам с дополнительными параметрами
    await send_searching_questions(
        message=message,
        state=state,
        my_response=my_response,
        tag=cleaned_text,
        another_key=f"user:{my_response['login']}:tag_queue_index",
        set_index=False
    )


# --- Кнопки действий при просмотре ленты вопросов по тегам --- #
@router.message(
    Searching.tape_tag_questions,
    (F.text == next_question) | (F.text == view_answers_question)
    (F.text == answer_question) | (F.text == vote_question) 
)
@anti_robot_check
@check_authorized
async def questions_tag_searching(message: Message, state: FSMContext, my_response: dict):
    data = await state.get_data()

    # Проверка на существование формы для заполнения
    if not data:
        await state.clear()
        return await message.answer(text=no_state, reply_markup=profile_kb())

    actions = {
        'view_answers': message.text in [view_answers_question],
        'vote': message.text in [vote_question],
        'create_answer': message.text in [answer_question]
    }

    await send_searching_questions(
        message=message,
        state=state,
        my_response=my_response,
        tag=data.get("tag", None),
        another_key=f"user:{my_response['login']}:tag_queue_index",
        **actions
    )


# --- Вернуться к просмотру вопросов --- #
@router.message((F.text == back_to_my_questions) | (F.text == back_to_global_questions))
async def back_to_question_tape_func(message: Message, state: FSMContext):
    # Если стадия существует, выходим из неё
    current_state = await state.get_state()
    if current_state is not None and\
    current_state != Searching.create_answer and\
    current_state != Searching.tape_answers and\
    current_state != EditQuestionOrAnswer.edit_question:
        await state.clear()

    data = await state.get_data()

    # Проверка на существование формы для заполнения
    if not data:
        await state.clear()
        return await message.answer(text=no_state, reply_markup=profile_kb())

    get_user_response_json = data.get('user_response', None)

    # Задаём новую стадию просмотра вопросов
    await state.set_state(Searching.tape_questions)

    # Возвращаемся к просмотру ленты
    await message.answer(
        text="🔎✨",
        reply_markup=all_questions_kb() if message.text == back_to_global_questions else my_questions_kb()
    )

    await send_searching_questions(
        message=message,
        state=state,
        my_response=get_user_response_json,
        set_index=False,
        global_tape=message.text == back_to_global_questions
    )
