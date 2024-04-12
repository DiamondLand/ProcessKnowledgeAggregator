import httpx
import asyncio

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from elements.inline.inline_admin import admins_btns
from elements.keyboards.keyboards_utilits import form_cancel_kb

from elements.answers import server_error

from events.states_group import Utilits

router = Router()


# --- Обработчик кнопки удаления логина ---
@router.callback_query(F.data == "delete_login")
async def delete_login(callback: CallbackQuery, state: FSMContext):
    await callback.answer(text="Вы безвозвратно удаляете аккаунт пользователю.", show_alert=True)
    await state.set_state(Utilits.delete_login)

    await callback.message.answer(
        text="‼ Пожалуйста, введите логин, аккаунт которого хотите <b>безвозвратно удалить</b>!",
        reply_markup=form_cancel_kb()
    )


# --- Обработчик сообщения и удаление аккаунта пользователя ---
@router.message(Utilits.delete_login)
async def stert_delete_login(message: Message, state: FSMContext):
    msg = await message.answer(text="Процесс удаления будет запущен через <i>5 секунд</i>. Вы можете <b>отменить</b> это действие <b>кнопкой под клавиатурой</b>!")
    await asyncio.sleep(5)  # Глушим на 5 секунд перед началом удаления

    # Если пользоветель отмменил, то останавливаем удаление
    if await state.get_state() != Utilits.delete_login:
        return

    async with httpx.AsyncClient() as client:
        delete_user_response = await client.delete(
            f"{message.bot.config['SETTINGS']['backend_url']}delete_user?login={message.text[:300]}"
        )

    await msg.delete()
    if delete_user_response.status_code == 200:
        if delete_user_response.json():
            await state.clear()
            await message.answer(text=f"Аккаунт <code>{message.text[:300]}</code> безвозвратно удалён!", reply_markup=ReplyKeyboardRemove())
            await message.answer("Вы - администратор", reply_markup=admins_btns().as_markup())
        else:
            await message.answer(text=f"Аккаунт <code>{message.text[:300]}</code> не найден! Повторите ввод:")
    else:
        await message.answer(text=server_error, reply_markup=form_cancel_kb())
