import httpx
import re

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from functions.inline_remove import remove_button
from functions.account.account_responses import check_account
from functions.account.account_data import delete_redis_keys
from functions.account.account_prefabs import prefab_account_blacklist

from elements.inline.inline_profile import finish_registration_btns
from elements.keyboards.keyboards_utilits import form_cancel_kb, generate_password_kb
from elements.keyboards.keyboards_profile import recreate_profile_kb, profile_kb

from elements.keyboards.text_on_kb import recreate_profile, reg_profile
from elements.answers import server_error, no_state

from events.states_group import CreateProfile

router = Router()


# --- Панель регистрации/пересоздания профиля -> логин ---
@router.message((F.text == reg_profile) | (F.text == recreate_profile))
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
        text=f"@{message.from_user.username}, придумай имя аккаунта (логин) до <b>40-а</b> символов:"
    )
    await state.set_state(CreateProfile.create_login)


# --- Стадия 1. Логин -> пароль --- #
@router.message(CreateProfile.create_login)
async def create_login(message: Message, state: FSMContext):
    data = await state.get_data()

    cleaned_text = re.sub(r'[<>]', '', message.text[:30]) # Убираем символы выделения
    data['login'] = cleaned_text
    await state.update_data(data)

    await message.answer(
        text=f"<b>Запомнил - <code>{cleaned_text}</code> ✨!</b>\
        \nТеперь потребуется пароль:\
        \n\n<i>* Случайно сгенерированный пароль отображён под клавиатруой. Вы можете воспользоваться им!</i>",
        reply_markup=generate_password_kb()
    )
    await state.set_state(CreateProfile.create_password)


# --- Стадия 2. Пароль -> Телефон --- #
@router.message(CreateProfile.create_password)
async def create_password(message: Message, state: FSMContext):
    data = await state.get_data()

    cleaned_text = re.sub(r'[<>]', '', message.text[:50]) # Убираем символы выделения
    data['password'] = cleaned_text
    await state.update_data(data)

    await message.answer(
        text=f"<b>Ваш пароль - <code>{cleaned_text}</code> ✨!</b>\
        \nУкажите контактую информацию:\
        \n\n<i>* Телефон или иное средство для связи.</i>",
        reply_markup=form_cancel_kb()
    )
    await state.set_state(CreateProfile.create_contacts)


# --- Стадия 3. Пароль -> финиш --- #
@router.message(CreateProfile.create_contacts)
async def create_contacts(message: Message, state: FSMContext):
    data = await state.get_data()

    if message.text and (message.text[0].isdigit() or message.text.startswith('+')):
        phone_number = re.sub(r'\D', '', message.text) # Оставить только цифры
        if len(phone_number) == 11:
            contact = f"+7 ({phone_number[1:4]}) {phone_number[4:7]}-{phone_number[7:9]}-{phone_number[9:]}"
        else:
            return await message.answer(
                text="❌ <b>Нет-нет-нет!</b>\
                    \n\nПохоже, Вы пытались указать номер телефона, но он должен состоять из <b>11 цифр</b>.\
                    \n\n<i>* Вы можете повторитеть попытку:</i>"
                )
    else:
        contact = message.text[:120]

    cleaned_text = re.sub(r'[<>]', '', contact) # Убираем символы выделения
    data['contacts'] = cleaned_text
    await state.update_data(data)

    await message.answer(
        text="Подытожим...",
        reply_markup=recreate_profile_kb()
    )
    await message.answer(
        text=f"\
        \n✅ Имя аккаунта (логин): <code>{data.get('login', '')}</code>\
        \n✅ Пароль: <code>{data.get('password', '')}</code>\
        \n✅ Способ связи: <code>{data.get('contacts', '')}</code>\
        \n\n<i>Не забудьте эти данные, они понадобятся для входа.</i>", 
        reply_markup=finish_registration_btns().as_markup()
    )


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
    # * .json() -> [{'user_info'}: ..., {'user_subsribes'}: ..., {'user_statistic'}: ..., {'user_privileges'}: ..., {'blacklist_info'}: ...]
    
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
        # Записываем в базу данные, введённые при регистрации
        async with httpx.AsyncClient() as client:
            create_user_response = await client.post(callback.bot.config["SETTINGS"]["backend_url"] + 'create_user', json={
                'user_id': callback.from_user.id,
                'login': data.get('login', ''),
                'password': data.get('password', None),
                'contacts': data.get('contacts', '')
            })

        if create_user_response.status_code == 200:
            if create_user_response.json():
                await state.clear()

                await callback.message.answer(
                    text=f"Добро пожаловать, @{callback.from_user.username}",
                    reply_markup=profile_kb()
                )
                await delete_redis_keys(msg=callback.message, user_id=callback.from_user.id)
            else:
                await callback.message.answer(text="❌ Логин и/или пароль уже заняты!")
        else:
            await callback.message.answer(text=server_error)
