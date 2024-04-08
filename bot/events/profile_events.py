import httpx

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from elements.keyboards.keyboards_profile import profile_kb
from elements.keyboards.keyboards_utilits import cancel_button

from .states_group import Captcha

router = Router()


# --- Завершение заполнения формы --- #
@router.message(F.text == cancel_button)
async def cancel_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == Captcha.captcha_input:
        return await message.answer(text="❌ Данное действие нельзя прервать!")

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

# --- Обработчик ввода каптчи --- #
@router.message(Captcha.captcha_input)
async def check_captcha(message: Message, state: FSMContext):
    data = await state.get_data()
    captcha_text = data.get('captcha_text', '')
    if message.text == captcha_text:
        await state.clear()
        await message.answer(
            text="Проверка на робота пройдена! Продолжим 😉?",
            reply_markup=profile_kb()
        )
    else:
        await message.answer(
            text=f"❌ Не верно! Повторите ввод: <strike><b>{captcha_text}</b></strike>",
            reply_markup=ReplyKeyboardRemove()
        )
