from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from functions.account.account_responses import check_account

from elements.keyboards.keyboards_profile import recreate_profile_kb

from elements.answers import server_error, banned, no_profile


# --- Проверка статусов --- #
async def prefab_account_statuses(msg: Message, user_id: int, state: FSMContext):
    user_moderation_response = await check_account(config=msg.bot.config, user_id=user_id)
    # * server_response
    # * server_response.json() -> {'user_info'}: ..., {'user_statistic'}: ..., {'user_privileges'}: ..., {'blacklist_info'}: ...

    if user_moderation_response.status_code == 200:
        # Если нет данных
        if user_moderation_response.json() is None or user_moderation_response.json()['user_info']:
            await msg.answer(
                text=no_profile,
                reply_markup=recreate_profile_kb()
            )
            return [user_moderation_response, {'message': 'user not found'}]
        else:
            return [user_moderation_response, None]
    else:
        await state.clear()
        await msg.answer(text=server_error)
        return [user_moderation_response, {'message': 'server_error'}]


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
            return [get_user_response, {'message': 'banned'}]

        return [get_user_response, None]
    else:
        await state.clear()
        await msg.answer(text=server_error, reply_markup=ReplyKeyboardRemove())
        return [get_user_response, {'message': 'server_error'}]
