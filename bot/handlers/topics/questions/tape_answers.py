import httpx
import re

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from decorators.profile_decorator import anti_robot_check

from functions.views_logic.looped_tape import send_searching_answers

from elements.keyboards.keyboards_answers import back_to_answers_kb
from elements.keyboards.keyboards_searching import all_answers_kb, my_answers_kb
from elements.keyboards.keyboards_profile import profile_kb

from elements.keyboards.text_on_kb import (next_my_answer, next_all_answer, vote_answer, back_to_my_answers, back_to_global_answers)

from elements.answers import no_state, server_error

from events.states_group import Searching, EditQuestionOrAnswer

router = Router()


# --- Кнопки действий при просмотре ленты ответов на вопрос --- #
@router.message(
    Searching.view_answers,
    (F.text == next_my_answer) | (F.text == next_all_answer) | (F.text == vote_answer)
)
@anti_robot_check
async def profile_searching(message: Message, state: FSMContext):
    data = await state.get_data()

    if not data:
        await state.clear()
        return await message.answer(text=no_state, reply_markup=profile_kb())
    
    my_response = data.get('user_response', None)
    global_tape = data.get('global_tape', True)
    question_id = data.get('question_id', None)
    
    actions = {
        'vote_answer': message.text in [vote_answer],
        'global_tape': global_tape
    }

    # Переходим в функцию просмотра ленты с дополнительными параметрами
    await send_searching_answers(
        message=message,
        state=state,
        question_id=question_id,
        my_response=my_response,
        **actions
    )


# --- Отправка ответа к вопросу --- #
@router.message(Searching.create_answer)
async def create_answer(message: Message, state: FSMContext):
    # Если стадия существует, выходим из неё
    current_state = await state.get_state()
    if current_state is not None and current_state != Searching.create_answer:
        await state.clear()

    data = await state.get_data()

    # Проверка на существование формы для заполнения
    if not data:
        await state.clear()
        return await message.answer(text=no_state, reply_markup=profile_kb())

    cleaned_text = re.sub(r'[<>]', '', message.text)  # Убираем символы выделения
    if len(cleaned_text) < 4 or len(cleaned_text) > 1000:
        return await message.answer(text="❌ Текст должен быть не короче 4 и не длиннее 1.000 символов! Пожалуйста, повтори ввод:")

    question_id = data.get('question_id', None)
    global_tape = data.get('global_tape', True)
    get_user_response_json = data.get('user_response', None)

    async with httpx.AsyncClient() as client:
        create_answer_response = await client.post(message.bot.config['SETTINGS']['backend_url'] + 'create_answer', json={
            "login": get_user_response_json['login'],
            "question_id": question_id,
            "answer": cleaned_text
        })

    if create_answer_response.status_code == 200:
        # Задаём новую стадию просмотра вопросов
        await state.set_state(Searching.tape_questions)

        # Возвращаемся к просмотру ленты
        await message.answer(
            text="🔎✨",
            reply_markup=all_answers_kb() if global_tape else my_answers_kb()
        )

        await send_searching_answers(
            message=message,
            state=state,
            question_id=question_id,
            my_response=get_user_response_json,
            global_tape=global_tape
        )
    else:
        await message.answer(text=server_error)
