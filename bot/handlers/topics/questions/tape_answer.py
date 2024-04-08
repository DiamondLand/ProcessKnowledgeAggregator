import re
import httpx
import random

from aiogram import Router, F
from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext

from functions.views_logic.looped_tape import send_searching_questrions

from elements.keyboards.keyboards_profile import profile_kb
from elements.keyboards.keyboards_searching import my_questions_kb, all_questions_kb

from elements.answers import server_error, no_state

from events.states_group import Searching

router = Router()


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
            reply_markup=all_questions_kb() if global_tape else my_questions_kb()
        )

        await send_searching_questrions(
            message=message,
            state=state,
            my_response=get_user_response_json,
            global_tape=global_tape
        )
    else:
        await message.answer(text=server_error)
