from aiogram import Router
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from decorators.profile_decorator import check_authorized
from decorators.admin_access_decorator import check_admin_access

from handlers.topics.questions.create_question import create_question_handler
from handlers.games.crossword import show_crossword

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

    await message.answer(
        text=f"<b>Добро пожаловать, дорогой {'администратор' if get_user_response['user_privileges']['is_admin'] else 'сотрудник'} ✨!</b>\
            \nВы вошли в аккаунт <code>{get_user_response['user_info']['login']}</code>!\
            \n\nВаших вопросов: <code>{get_user_response['user_statistic']['questions']}</code> | Ваших ответов: <code>{get_user_response['user_statistic']['answers']}</code>\
            \nВаших поинтов: <code>{get_user_response['user_statistic']['points']}</code>",
        reply_markup=profile_kb())


@router.message(Command("game"))
@check_authorized
async def cmd_game(message: Message, state: FSMContext, __get_user_response: dict):
    # Если стадия существует, выходим из неё
    if await state.get_state() is not None:
        await state.clear()

    await message.answer("Давайте сыграем в кроссворд по теме <code>машиностроения</code>. Вот карта кроссворда:")
    await show_crossword(message=message, state=state)


# --- Задать вопрос --- #
@router.message(Command("question"))
@check_authorized
async def cmd_question(message: Message, state: FSMContext, __get_user_response: dict):
    # Если стадия существует, выходим из неё
    if await state.get_state() is not None:
        await state.clear()

    await create_question_handler(message=message, state=state)


# --- Админская панель --- #
@router.message(Command("admin"))
@check_admin_access
async def cmd_admin(message: Message, state: FSMContext, __get_user_response: dict):
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
