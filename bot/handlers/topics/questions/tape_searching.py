from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from decorators.profile_decorator import check_authorized

from functions.views_logic.looped_tape import send_searching_questrions

from elements.keyboards.keyboards_searching import my_questions_kb, all_questions_kb
from elements.keyboards.text_on_kb import my_questions, all_questions

from events.states_group import Searching

router = Router()


# --- Кнопка просмотра ленты вопросов ---
@router.message((F.text == my_questions) | (F.text == all_questions))
@check_authorized
async def start_questions_searching(message: Message, state: FSMContext, get_user_response_json: dict):
    # Если стадия существует, выходим из неё
    if await state.get_state() is not None:
        await state.clear()

    await state.set_state(Searching.tape_questions)

    # Отправялем эмодзи и задаём keyboard
    await message.answer(
        text="🔎✨",
        reply_markup=my_questions_kb() if message.text == my_questions else all_questions_kb()
    )

    # Переходим в функцию просмотра ленты
    await send_searching_questrions(
        message=message,
        state=state,
        my_response=get_user_response_json,
        set_index=False,
        global_tape=message.text == all_questions
    )
