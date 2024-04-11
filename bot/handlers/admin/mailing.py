import httpx
import asyncio

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from elements.keyboards.keyboards_utilits import form_cancel_kb
from elements.answers import server_error
from events.states_group import Utilits

router = Router()


# --- Обработчик кнопки рассылки ---
@router.callback_query(F.data == "mailing")
async def mailing(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Utilits.mailing)

    await callback.message.answer(
        text="‼ Пожалуйста, введите текст, который будет разослан <b>всем пользователям</b>:",
        reply_markup=form_cancel_kb()
    )


# --- Обработчик сообщения и рассылка всем пользователям ---
@router.message(Utilits.mailing)
async def mailing_send(message: Message, state: FSMContext):

    msg = await message.answer(text="Процесс отправки будет запущен через <i>5 секунд</i>. Вы можете <b>отменить</b> это действие <b>кнопкой под клавиатурой</b>!")
    await asyncio.sleep(5)  # Глушим на 10 секунд перед началом рассылки

    # Если пользоветель отмменил, то останавливаем рассылку
    if await state.get_state() != Utilits.mailing:
        return

    async with httpx.AsyncClient() as client:
        get_users_response = await client.get(
            f"{message.bot.config['SETTINGS']['backend_url']}get_users"
        )
    # * .json() -> [{'user_info'}: ..., {'user_subsribes'}: ..., {'user_statistic'}: ..., {'user_privileges'}: ..., {'blacklist_info'}: ...]

    if get_users_response.status_code == 200 and get_users_response.json():

        counter = 0
        await msg.delete()
        await message.answer(
            text=f"<b>Рассылка запущена!</b>", 
            reply_markup=ReplyKeyboardRemove()
        )

        for user_info in get_users_response.json():
            try:
                await message.bot.send_message(
                    chat_id=user_info['user_info']['user_id'],  # используем контакты пользователя в качестве chat_id
                    text=f"Рассылка от @{message.from_user.username}:\n—\n{message.text}"
                )
                counter += 1
            except:
                pass

        await state.clear()
        await message.answer(text=f"<b>Рассылка закончена!</b>\n\nОтправлено {counter}/{len(get_users_response.json())}.")
    else:
        await message.answer(text=server_error, reply_markup=form_cancel_kb())
