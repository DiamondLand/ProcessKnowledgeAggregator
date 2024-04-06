from aiogram.types import Message
from aiogram.fsm.context import FSMContext


async def remove_button(msg: Message, inline_keyboard_markup = None, state: FSMContext = None):
    try:
        await msg.edit_reply_markup(reply_markup=inline_keyboard_markup)
        if state:
            await state.clear()
    except:
        pass
