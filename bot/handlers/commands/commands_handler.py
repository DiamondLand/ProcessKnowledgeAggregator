from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from decorators.profile_decorator import check_authorized

from elements.keyboards.keyboards_profile import profile_kb

router = Router()


# --- Главная панель --- #
@router.message(Command("start", "profile"))
@check_authorized
async def cmd_start(message: Message, state: FSMContext, get_user_response: dict):
    # Если стадия существует, выходим из неё
    if await state.get_state() is not None:
        await state.clear()

    await message.answer(text=f"<b>Добро пожаловать 🔎!</b>\n\nВы вошли под как <code>{get_user_response['login']}</code>!", reply_markup=profile_kb())


# --- Информационная панель --- #
@router.message(Command("info"))
async def cmd_info(message: Message, state: FSMContext):
    # Если стадия существует, выходим из неё
    if await state.get_state() is not None:
        await state.clear()
    
    await message.answer(text=f"...")


# --- Админская панель --- #
@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext):
    # Если стадия существует, выходим из неё
    if await state.get_state() is not None:
        await state.clear()

    await message.answer(text=f"...")
