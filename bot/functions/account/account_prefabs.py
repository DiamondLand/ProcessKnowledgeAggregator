from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from elements.keyboards.keyboards_profile import reg_or_auth_kb

from elements.answers import server_error, banned, no_authorized


# --- Проверка на авторизацию --- #
async def prefab_account_check_authorized(msg: Message, state: FSMContext, get_user_response: dict):
    if get_user_response.status_code == 200:
        if get_user_response.json()['user_info'] is None or 'is_authorized' in get_user_response.json()['user_info']:
            await msg.answer(
                text=no_authorized,
                reply_markup=reg_or_auth_kb()
            )
            await state.clear()
            return [get_user_response, {'message': 'user not authorized'}]
        else:
            return [get_user_response, None]
    else:
        await state.clear()
        await msg.answer(text=server_error)
        return [get_user_response, {'message': 'server_error'}]


# --- Проверка на чёрный список --- #
async def prefab_account_blacklist(msg: Message, user_id: int, state: FSMContext, get_user_response: dict):
    if get_user_response.status_code == 200:
        if get_user_response.json()['blacklist_info'] and user_id not in msg.bot.permanent_ids:
            await state.clear()

            await msg.answer(
                text=banned.format(
                    reason=get_user_response.json()['blacklist_info']['reason']
                ),
                reply_markup=ReplyKeyboardRemove()
            )
            await state.clear()
            return [get_user_response, {'message': 'banned'}]

        return [get_user_response, None]
    else:
        await state.clear()
        await msg.answer(text=server_error, reply_markup=ReplyKeyboardRemove())
        return [get_user_response, {'message': 'server_error'}]
