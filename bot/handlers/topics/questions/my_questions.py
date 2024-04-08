import httpx
import re

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from functions.inline_remove import remove_button
from functions.account.account_data import delete_redis_keys
from functions.account.account_prefabs import prefab_account_blacklist

from decorators.profile_decorator import check_authorized

from elements.keyboards.keyboards_profile import recreate_profile_kb, profile_kb

from elements.keyboards.text_on_kb import my_questions
from elements.answers import server_error, no_state

router = Router()


# --- Панель просмотра заданных вопросов ---
@router.message(F.text == my_questions)
@check_authorized
async def my_question_btn(message: Message, state: FSMContext, get_user_response: dict):
    # Если стадия существует, выходим из неё
    if await state.get_state() is not None:
        await state.clear()

    # Проверка аккаунта по логину
    async with httpx.AsyncClient() as client:
        all_user_questions_response = await client.get(
            f"{message.bot.config['SETTINGS']['backend_url']}get_all_user_questions?login={get_user_response['login']}"
        )
    
    if all_user_questions_response.status_code == 200:
        if all_user_questions_response.json():
            
        else:
            # :TODO: Сделать создание вопроса
            await message.answer(text="<b>У вас нет заданных вопросов 🧐!</b>\nПри возникновении трудностей создайте новый вопрос по кнопке ниже:")
    else:
        await message.answer(text=server_error)