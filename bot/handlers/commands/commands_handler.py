from aiogram import Router
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from decorators.profile_decorator import check_authorized
from decorators.admin_access_decorator import check_admin_access

from handlers.topics.questions.create_question import create_question_handler

from elements.inline.inline_admin import admins_btns
from elements.keyboards.keyboards_profile import profile_kb

router = Router()


# --- Главная панель --- #
@router.message(Command("start", "profile"))
@check_authorized
async def cmd_start(message: Message, state: FSMContext, get_user_response: dict):
    # Если стадия существует, выходим из неё
    if await state.get_state() is not None:
        await state.clear()

    await message.answer(text=f"<b>Добро пожаловать 😉!</b>\n\nВы вошли как <code>{get_user_response['login']}</code>!", reply_markup=profile_kb())


# --- Задать вопрос --- #
@router.message(Command("question"))
@check_authorized
async def cmd_question(message: Message, state: FSMContext, get_user_response: dict):
    # Если стадия существует, выходим из неё
    if await state.get_state() is not None:
        await state.clear()

    await create_question_handler(message=message, state=state)


# --- Информационная панель --- #
@router.message(Command("info"))
async def cmd_info(message: Message, state: FSMContext):
    # Если стадия существует, выходим из неё
    if await state.get_state() is not None:
        await state.clear()
    
    await message.answer(text=f"...")


# --- Админская панель --- #
@router.message(Command("admin"))
@check_admin_access
async def cmd_admin(message: Message, state: FSMContext, get_user_response: dict):
    # Если стадия существует, выходим из неё
    if await state.get_state() is not None:
        await state.clear()

    await message.answer(
        text="🕐 Секундочку...",
        reply_markup=ReplyKeyboardRemove()
    )
    await message.answer(
        text="Вы - администратор!",
        reply_markup=admins_btns().as_markup()
    )
