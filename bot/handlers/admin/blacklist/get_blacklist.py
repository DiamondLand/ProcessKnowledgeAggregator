import httpx

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.exceptions import TelegramBadRequest

from elements.inline.inline_admin import admins_btns
from elements.answers import server_error

router = Router()


# --- Отображение чёрного списка --- #
@router.callback_query(F.data == "get_blacklist")
async def get_blacklist(callback: CallbackQuery):
    async with httpx.AsyncClient() as client:
        get_blacklist_response = await client.get(
            f"{callback.bot.config['SETTINGS']['backend_url']}get_blacklist"
        )

    if get_blacklist_response.status_code != 200:
        return await callback.message.edit_text(text=server_error)

    if get_blacklist_response.json():
        formatted_entries = '\n\n'.join([
            f"Пользователь: <code>{entry['login']}</code>, Причина: <code>{entry['reason']}</code>"
            for _, entry in enumerate(get_blacklist_response.json(), start=1)

        ])

        try:
            await callback.message.edit_text(
                text=formatted_entries,
                reply_markup=admins_btns().as_markup()
            )
        except TelegramBadRequest:  # Если текст не изменился
            await callback.message.edit_text(
                text="Вы - администратор",
                reply_markup=admins_btns().as_markup()
            )
    else:
        try:
            await callback.message.edit_text(
                text="✨ Чёрный список пуст!",
                reply_markup=admins_btns().as_markup()
            )
        except TelegramBadRequest:  # Если текст не изменился
            await callback.message.edit_text(
                text="Вы - администратор",
                reply_markup=admins_btns().as_markup()
            )
