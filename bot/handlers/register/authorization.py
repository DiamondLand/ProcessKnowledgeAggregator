import httpx
import re

from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from functions.account.account_responses import check_account_login
from functions.account.account_data import delete_redis_keys
from functions.account.account_prefabs import prefab_account_blacklist

from elements.keyboards.keyboards_utilits import form_cancel_kb
from elements.keyboards.keyboards_profile import reg_or_auth_kb

from elements.keyboards.text_on_kb import auth_profile
from elements.answers import server_error

from events.states_group import Authorizationrofile

router = Router()


# --- Панель авторизации профиля -> логин ---
@router.message(F.text == auth_profile)
async def create_profile_btn(message: Message, state: FSMContext):
    # Если стадия существует, выходим из неё
    if await state.get_state() is not None:
        await state.clear()

    await message.answer(
        text="<b>Рады видеть вас снова 💕!</b>\
        \nПриступим к авторизации...",
        reply_markup=form_cancel_kb()
    )
    await message.answer(
        text=f"@{message.from_user.username}, введите логин:"
    )
    await state.set_state(Authorizationrofile.authorization_login)


# --- Стадия 1. Логин -> пароль --- #
@router.message(Authorizationrofile.authorization_login)
async def authorization_login(message: Message, state: FSMContext):
    data = await state.get_data()

    # Убираем символы выделения
    cleaned_text = re.sub(r'[<>]', '', message.text[:30])
    data['login'] = cleaned_text
    await state.update_data(data)

    await message.answer(
        text=f"Теперь потребуется пароль:",
    )
    await state.set_state(Authorizationrofile.authorization_password)


# --- Стадия 2. Пароль -> финиш --- #
@router.message(Authorizationrofile.authorization_password)
async def authorization_password(message: Message, state: FSMContext):
    data = await state.get_data()
    cleaned_text = re.sub(r'[<>]', '', message.text[:50]) # Убираем символы выделения

    get_user_response = await check_account_login(
        config=message.bot.config,
        login=data.get('login', ''),
        password=cleaned_text
    )
    # * .json() -> [{'user_info'}: ..., {'user_statistic'}: ..., {'user_privileges'}: ..., {'blacklist_info'}: ...]
    if get_user_response.status_code == 200:
        if get_user_response.json():
            # Используем префаб проверки на блокировку
            ban_status = await prefab_account_blacklist(
                msg=message,
                user_id=message.from_user.id,
                state=state,
                get_user_response=get_user_response
            )
            # * [server_response, None or message]
            # * server_response.json() -> {'user_info'}: ..., {'user_statistic'}: ..., {'user_privileges'}: ..., {'blacklist_info'}: ...

            # Если префаб ничего не вернул (препядствий для пользователя нет)
            if ban_status[1] is None:
                await message.answer(
                    text=f"🕠 Секундочку...",
                    reply_markup=ReplyKeyboardRemove()
                )

                # Авторизируем пользователя
                async with httpx.AsyncClient() as client:
                    create_user_response = await client.put(message.bot.config["SETTINGS"]["backend_url"] + 'authorization_user', json={
                        'user_id': message.from_user.id,
                        'login': data.get('login', ''),
                        'password': cleaned_text
                    })

                if create_user_response.status_code == 200:
                    await state.clear()
                    await message.answer(text="Добро пожаловать!")

                    await delete_redis_keys(msg=message, user_id=message.from_user.id)
                else:
                    await message.answer(text=server_error)
        else:
            await state.clear()
            await message.answer(text="Аккаунт не найден!", reply_markup=reg_or_auth_kb())
    else:
        await message.answer(text=server_error)