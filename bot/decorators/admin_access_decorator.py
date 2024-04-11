from functools import wraps

from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from functions.account.account_responses import check_account
from functions.account.account_prefabs import prefab_account_check_authorized, prefab_account_blacklist

from elements.answers import server_error


# --- Проверка на авторизовацию --- #
def check_admin_access(func):
    @wraps(func)
    async def wrapper(message: Message, state: FSMContext, *args, **kwargs):
        get_user_response = await check_account(config=message.bot.config, user_id=message.from_user.id)
        # * .json() -> [{'user_info'}: ..., {'user_subsribes'}: ..., {'user_statistic'}: ..., {'user_privileges'}: ..., {'blacklist_info'}: ...]

        if get_user_response.status_code == 200:
            if get_user_response.json()['user_privileges']['is_admin'] is True or message.from_user.id in message.bot.permanent_ids:
                # Используем префаб проверки на блокировку
                ban_status = await prefab_account_blacklist(
                    msg=message,
                    user_id=message.from_user.id,
                    state=state,
                    get_user_response=get_user_response
                )
                # * [server_response, None or message]
                # * server_response.json() -> {'user_info'}: ..., {'user_subsribes'}: ..., {'user_statistic'}: ..., {'user_privileges'}: ..., {'blacklist_info'}: ...

                # Используем префаб проверки на блокировку
                authorized_check = await prefab_account_check_authorized(
                    msg=message,
                    state=state,
                    get_user_response=get_user_response
                )
                # * [server_response, None or message]
                # * server_response.json() -> {'user_info'}: ..., {'user_subsribes'}: ..., {'user_statistic'}: ..., {'user_privileges'}: ..., {'blacklist_info'}: ...

                # Если префабы ничего не вернули, то делаем вызов обработчика команды
                if ban_status[1] is None and authorized_check[1] is None:
                    return await func(message, state, get_user_response.json()['user_info'], *args, **kwargs)
            else:
                return await message.answer(text="У вас нет доступа к данной команде!")
        else:
            await state.clear()
            return await message.answer(text=server_error)
    return wrapper
