from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from decorators.profile_decorator import check_authorized, anti_robot_check

from functions.views_logic.looped_tape import send_searching_questrions

from elements.keyboards.text_on_kb import (next_my_question, next_question, answer_my_question, answer_question, edit_my_question, vote_question)

from events.states_group import Searching

router = Router()


# --- Кнопки действий при просмотре ленты вопросов --- #
@router.message(
        Searching.tape_questions, 
        (F.text == next_my_question) | (F.text == next_question) |
        (F.text == answer_my_question) | (F.text == answer_question) |
        (F.text == edit_my_question) | (F.text == vote_question))
@anti_robot_check
@check_authorized
async def profile_searching(message: Message, state: FSMContext, my_response: dict):
    # Если стадия существует, выходим из неё
    current_state = await state.get_state()
    if current_state is not None and current_state != Searching.tape_questions:
        await state.clear()

    actions = {
        'edit_question': message.text in [edit_my_question],
        'create_answer': message.text in [answer_my_question, answer_question],
        'global_tape': message.text in [next_question, answer_question]
    }
    # Переходим в функцию просмотра ленты с дополнительными параметрами: лайк / жалоба
    await send_searching_questrions(
        message=message,
        state=state,
        my_response=my_response,
        **actions
    )
