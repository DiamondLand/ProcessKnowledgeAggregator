import httpx

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from elements.keyboards.keyboards_utilits import cancel_button

router = Router()


# --- Завершение заполнения формы --- #
@router.message(F.text == cancel_button)
async def cancel_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()

    if current_state is None:
        return await message.answer(
            text="Нет действий, которые можно было бы прервать!",
            reply_markup=ReplyKeyboardRemove()
        )

    await state.clear()
    await message.answer(
        text="<b>Действие прервано!</b>\n\nДля возвращения в главную панель воспользуйтесь /profile!",
        reply_markup=ReplyKeyboardRemove()
    )
