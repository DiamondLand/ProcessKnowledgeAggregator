from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from decorators.admin_access_decorator import check_admin_access

from functions.inline_remove import remove_button
from functions.views_logic.solo_tape import send_moder_tape

from elements.keyboards.keyboards_searching import admin_tape_kb

from elements.keyboards.text_on_kb import moder_no, moder_yes

from events.states_group import Searching

router = Router()


# --- Просмотр ленты ---
@router.callback_query(F.data == "moder_question")
async def moder_question(callback: CallbackQuery, state: FSMContext):
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
        question=True
    )


# --- Кнопка одбрения/не одобрения для просмотра ---
@router.message(Searching.tape_moder_questions, (F.text == moder_no) | (F.text == moder_yes))
@check_admin_access
async def start_moder_tape(message: Message, state: FSMContext):
    await send_moder_tape(
        state=state,
        message=message,
        questions=True
    )
