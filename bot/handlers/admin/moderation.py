from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from functions.inline_remove import remove_button
from functions.views_logic.solo_tape import send_moder_tape

from elements.keyboards.keyboards_searching import admin_tape_kb

from elements.keyboards.text_on_kb import moder_no, moder_yes

from events.states_group import Searching

router = Router()


# --- Просмотр ленты модерации вопросов ---
@router.callback_query(F.data == "moder_questions")
async def moder_questions(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Searching.tape_moder_questions)
    
    await remove_button(msg=callback.message, inline_keyboard_markup=None)

    await callback.message.answer(
        text="💬✨",
        reply_markup=admin_tape_kb()
    )

    await send_moder_tape(
        state=state,
        callback=callback,
        set_index=False,
        questions=True
    )


# --- Кнопка одбрения/не одобрения вопросов ---
@router.message(Searching.tape_moder_questions, (F.text == moder_no) | (F.text == moder_yes))
async def start_questions_moder_tape(message: Message, state: FSMContext):
    actions = {
        'reject': message.text in [moder_no],
        'accept': message.text in [moder_yes],
    }

    await send_moder_tape(
        state=state,
        message=message,
        questions=True,
        **actions
    )


# --- Просмотр ленты модерации ответов ---
@router.callback_query(F.data == "moder_answers")
async def moder_answers(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Searching.tape_moder_answers)
    
    await remove_button(msg=callback.message, inline_keyboard_markup=None)

    await callback.message.answer(
        text="💬✨",
        reply_markup=admin_tape_kb()
    )

    await send_moder_tape(
        state=state,
        callback=callback,
        set_index=False,
        answers=True
    )


# --- Кнопка одбрения/не одобрения ответов ---
@router.message(Searching.tape_moder_answers, (F.text == moder_no) | (F.text == moder_yes))
async def start_answers_moder_tape(message: Message, state: FSMContext):
    actions = {
        'reject': message.text in [moder_no],
        'accept': message.text in [moder_yes],
    }

    await send_moder_tape(
        state=state,
        message=message,
        answers=True,
        **actions
    )
