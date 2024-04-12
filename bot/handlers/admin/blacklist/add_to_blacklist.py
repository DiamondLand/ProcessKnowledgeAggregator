import httpx
import re

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from elements.inline.inline_admin import admins_btns
from elements.answers import server_error, no_state

from events.states_group import AddRemoveBlacklist

router = Router()


# --- Добавление в чёрный спискок -> Ввод Id --- #
@router.callback_query(F.data == "add_to_blacklist")
async def add_to_blacklist(callback: CallbackQuery, state: FSMContext):
    await callback.answer(text="Вы вносите пользователя в чёрный список.", show_alert=True)
    await callback.message.answer(
        text="✨💬",
        reply_markup=ReplyKeyboardRemove()
    )

    # Если стадия существует, выходим из неё
    if await state.get_state() is not None:
        await state.clear()

    await callback.message.answer(text="Введите логин для добавления в чёрный список:")
    await state.set_state(AddRemoveBlacklist.blacklist_login_to_add)


# --- Чёрный спискок -> Ввод логина --- #
@router.message(AddRemoveBlacklist.blacklist_login_to_add)
async def blacklist_login_to_add(message: Message, state: FSMContext):
    data = await state.get_data()

    cleaned_text = re.sub(r'[<>]', '', message.text[:300]) # Убираем символы выделения
        
    data['login_to_blacklist'] = cleaned_text
    await state.update_data(data)

    await message.answer(text="Введите причину для добавления в чёрный список:")
    await state.set_state(AddRemoveBlacklist.blacklist_reason)


# --- Ввод логина -> ввод причины и финиш --- #
@router.message(AddRemoveBlacklist.blacklist_reason)
async def blacklist_reason(message: Message, state: FSMContext):
    data = await state.get_data()

    # Проверка на сохранение данных
    if not data:
        await state.clear()
        return await message.answer(text=no_state, reply_markup=admins_btns().as_markup())
    
    # Убираем символы выделения
    cleaned_text = re.sub(r'[<>]', '', message.text[:300])
    login_to_blacklist = data.get('login_to_blacklist', None)

    async with httpx.AsyncClient() as client:
        input_to_blacklist_response = await client.post(
            message.bot.config["SETTINGS"]["backend_url"] + 'add_to_blacklist', json={
                'login': login_to_blacklist,
                'reason': cleaned_text
            }
        )

    if input_to_blacklist_response.status_code != 200:
        return await message.answer(text=server_error)

    await state.clear()
    await message.answer(
        text=f"✅ Пользователь <code>{login_to_blacklist}</code> занесён в чёрный список!",
        reply_markup=admins_btns().as_markup()
    )
