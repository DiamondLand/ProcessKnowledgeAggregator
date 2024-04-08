import httpx
import re

from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.fsm.context import FSMContext

from functions.inline_remove import remove_button
from functions.account.account_responses import check_account
from functions.account.account_data import delete_redis_keys
from functions.account.account_prefabs import prefab_account_blacklist

from elements.inline.inline_profile import finish_registration_btns
from elements.keyboards.keyboards_utilits import form_cancel_kb
from elements.keyboards.keyboards_profile import recreate_profile_kb

from elements.keyboards.text_on_kb import auth_profile
from elements.answers import server_error, no_state

from events.states_group import Authorizationrofile

router = Router()


# --- Панель авторизации профиля -> логин ---
@router.message(F.text == auth_profile)
async def create_profile_btn(message: Message, state: FSMContext):
    # Если стадия существует, выходим из неё
    if await state.get_state() is not None:
        await state.clear()

    await message.answer(
        text="<b>Добро пожаловать 💕!</b>\
        \nПриступим к регистрации...",
        reply_markup=form_cancel_kb()
    )
    await message.answer(
        text=f"@{message.from_user.username}, придумай логин до <b>40-а</b> символов:"
    )
    await state.set_state(Authorizationrofile.authorization_login)


# --- Стадия 1. Логин -> пароль --- #
@router.message(Authorizationrofile.authorization_login)
async def authorization_login(message: Message, state: FSMContext):
    data = await state.get_data()

    cleaned_text = re.sub(r'[<>]', '', message.text[:30]) # Убираем символы выделения
    data['login'] = cleaned_text
    await state.update_data(data)

    # :TODO: Длбавить генерацию пароля
    await message.answer(
        text=f"<b>Запомнил - <code>{cleaned_text}</code> ✨!</b>\
        \nТеперь потребуется пароль:",
    )
    await state.set_state(Authorizationrofile.authorization_password)


# --- Стадия 2. Пароль -> финиш --- #
@router.message(Authorizationrofile.authorization_password)
async def authorization_password(message: Message, state: FSMContext):
    data = await state.get_data()

    cleaned_text = re.sub(r'[<>]', '', message.text[:50]) # Убираем символы выделения
    data['password'] = cleaned_text
    await state.update_data(data)



# --- Стадия 4. Финал --- #
@router.callback_query(F.data == "finish_registration")
async def finish_registration(callback: CallbackQuery, state: FSMContext):# -
    data = await state.get_data()

    # Удаляем кнопку с сообщения
    await remove_button(msg=callback.message, state=state)

    # Проверка на сохранение данных. Берём самое последнее (contacts)
    if not data.get('contacts', ''):
        await state.clear()
        return await callback.message.answer(text=no_state)

    get_user_response = await check_account(config=callback.bot.config, user_id=callback.from_user.id)
    # * .json() -> [{'user_info'}: ..., {'user_statistic'}: ..., {'user_privileges'}: ..., {'blacklist_info'}: ...]
    
    # Используем префаб проверки на блокировку
    ban_status = await prefab_account_blacklist(
        msg=callback.message,
        user_id=callback.from_user.id,
        state=state,
        get_user_response=get_user_response
    )
    # * [server_response, None or message]
    # * server_response.json() -> {'user_info'}: ..., {'user_statistic'}: ..., {'user_privileges'}: ..., {'blacklist_info'}: ...

    # Если префаб ничего не вернул (препядствий для пользователя нет)
    if ban_status[1] is None:
        await callback.message.answer(
            text=f"🕠 Секундочку...", 
            reply_markup=ReplyKeyboardRemove()
        )

        # Записываем в базу данные, введённые при регистрации
        async with httpx.AsyncClient() as client:
            create_user_response = await client.post(callback.bot.config["SETTINGS"]["backend_url"] + 'create_user', json={
                'user_id': callback.from_user.id,
                'login': data.get('login', ''),
                'password': data.get('password', None),
                'contacts': data.get('contacts', '')
            })

        if create_user_response.status_code == 200:
            await state.clear()

            # :TODO: Перебрасывать в панель аккаунта
            await callback.message.answer(text="Добро пожаловать!")

            await delete_redis_keys(msg=callback.message, user_id=callback.from_user.id)
        else:
            await callback.message.answer(text=server_error)
