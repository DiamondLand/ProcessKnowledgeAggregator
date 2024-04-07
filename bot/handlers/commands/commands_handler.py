from aiogram import Router
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from elements.keyboards.keyboards_profile import recreate_profile_kb

router = Router()


# --- Главная панель --- #
@router.message(Command("start", "profile"))
async def cmd_start(message: Message, state: FSMContext):
    # Если стадия существует, выходим из неё
    if await state.get_state() is not None:
        await state.clear()

    await message.answer(text=f"...", reply_markup=recreate_profile_kb())


# --- Информационная панель --- #
@router.message(Command("info"))
async def cmd_info(message: Message, state: FSMContext):
    # Если стадия существует, выходим из неё
    if await state.get_state() is not None:
        await state.clear()
    
    await message.answer(text=f"...")


# --- Админская панель --- #
@router.message(Command("admin", "bin"))
async def cmd_admin(message: Message, state: FSMContext):
    # Если стадия существует, выходим из неё
    if await state.get_state() is not None:
        await state.clear()

    await message.answer(text=f"...")
