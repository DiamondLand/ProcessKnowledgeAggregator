from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from elements.keyboards.keyboards_utilits import form_cancel_kb

from functions.account.account_responses import check_account_login

from elements.answers import server_error, no_state

from events.states_group import Utilits

router = Router()


# --- Обработчик кнопки отправки послания ---
@router.callback_query(F.data == "send_dm")
async def send_dm(callback: CallbackQuery, state: FSMContext):
    await callback.answer(text="Вы находитесь в отправке личных сообщений.", show_alert=True)
    await state.set_state(Utilits.send_dm_get_login)

    await callback.message.answer(
        text="💕 Пожалуйста, введите логин аккаунта, которому хотите отправить сообщение:",
        reply_markup=form_cancel_kb()
    )


# --- Ввод логина -> воод сообщения ---
@router.message(Utilits.send_dm_get_login)
async def send_dm_get_login(message: Message, state: FSMContext):
    get_user_response = await check_account_login(
        config=message.bot.config,
        login=message.text[:300]
    )
    # * .json() -> [{'user_info'}: ..., {'user_subsribes'}: ..., {'user_statistic'}: ..., {'user_privileges'}: ..., {'blacklist_info'}: ...]

    if get_user_response.status_code == 200:
        if get_user_response.json()['user_info']:

            data = await state.get_data()
            data['get_user_response'] = get_user_response.json()
            await state.update_data(data=data)

            await state.set_state(Utilits.send_dm)

            await message.answer(
                text="💌 Пожалуйста, введите сообщение, которое хотите отправить пользователю:",
                reply_markup=form_cancel_kb()
            )
        else:
            await message.answer(text=f"Аккаунт <code>{message.text[:300]}</code> не найден! Повторите ввод:")
    else:
        await message.answer(text=server_error, reply_markup=form_cancel_kb())
    

# --- Воод сообщения -> отправка сообщения ---
@router.message(Utilits.send_dm)
async def start_send_dm(message: Message, state: FSMContext):
    data = await state.get_data()
    
    if not data:
        await state.clear()
        return await message.answer(text=no_state)
    
    get_user_response = data['get_user_response']
    await state.clear()

    try:
        await message.bot.send_message(
            chat_id=get_user_response['user_info']['user_id'],
            text=f"<b>💌 Новое сообщение от администрации!</b>\
                \n-\
                \n{message.text[:1000]}"
        )
        await message.answer(
            text="💖 Пользователь получил ваше сообщение!",
            reply_markup=ReplyKeyboardRemove()
        )
    except:
        await message.answer(
            text="💔 Пользователь не получил сообщение, поскольку не был авторизован/удалил чат с ботов.",
            reply_markup=ReplyKeyboardRemove()
        )
