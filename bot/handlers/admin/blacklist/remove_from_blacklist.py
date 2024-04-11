import httpx
import re

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from elements.inline.inline_admin import admins_btns
from elements.answers import server_error

from events.states_group import AddRemoveBlacklist

router = Router()


# --- Вычёркивание из чёрного списка -> Ввод логин --- #
@router.callback_query(F.data == "remove_from_blacklist")
async def remove_from_blacklist(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        text="✨💬",
        reply_markup=ReplyKeyboardRemove()
    )

    # Если стадия существует, выходим из неё
    if await state.get_state() is not None:
        await state.clear()

    await callback.message.answer(text="Введите логин для вычёркивания из чёрного списка:")
    await state.set_state(AddRemoveBlacklist.blacklist_login_to_remove)


# --- Ввод логина -> ввод причины и финиш --- #
@router.message(AddRemoveBlacklist.blacklist_login_to_remove)
async def input_id_to_remove_from_blacklist(message: Message, state: FSMContext):    
    cleaned_text = re.sub(r'[<>]', '', message.text[:300]) # Убираем символы выделения

    async with httpx.AsyncClient() as client:
        input_to_blacklist_response = await client.delete(
            f'{message.bot.config["SETTINGS"]["backend_url"]}delete_from_blacklist?login={cleaned_text}'
        )

    if input_to_blacklist_response.status_code != 200:
        return await message.answer(text=server_error)

    if input_to_blacklist_response.json():
        await state.clear()
        await message.answer(
            text=f"✅ Пользователь <code>{cleaned_text}</code> вычеркнут из в чёрного списка!",
            reply_markup=admins_btns().as_markup()
        )
    else:
        await message.answer(text=f"❗ Пользователь <code>{cleaned_text}</code> не находится в чёрном списке! Повтори ввод:")
