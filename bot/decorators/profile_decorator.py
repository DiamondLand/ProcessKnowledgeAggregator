from functools import wraps

from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from functions.account.account_responses import check_account
from functions.account.account_prefabs import prefab_account_check_authorized, prefab_account_blacklist
from functions.captcha.captha_suspected import is_suspected_robot, handle_suspected_robot

from elements.answers import server_error


# --- Проверка на авторизовацию --- #
def check_authorized(func):
    @wraps(func)
    async def wrapper(message: Message, state: FSMContext, *args, **kwargs):
        get_user_response = await check_account(config=message.bot.config, user_id=message.from_user.id)
        # * .json() -> [{'user_info'}: ..., {'user_statistic'}: ..., {'user_privileges'}: ..., {'blacklist_info'}: ...]

        if get_user_response.status_code == 200:
            # Используем префаб проверки на блокировку
            ban_status = await prefab_account_blacklist(
                msg=message,
                user_id=message.from_user.id,
                state=state,
                get_user_response=get_user_response
            )
            # * [server_response, None or message]
            # * server_response.json() -> {'user_info'}: ..., {'user_statistic'}: ..., {'user_privileges'}: ..., {'blacklist_info'}: ...
            
            # Используем префаб проверки на блокировку
            authorized_check = await prefab_account_check_authorized(
                msg=message,
                state=state,
                get_user_response=get_user_response
            )
            # * [server_response, None or message]
            # * server_response.json() -> {'user_info'}: ..., {'user_statistic'}: ..., {'user_privileges'}: ..., {'blacklist_info'}: ...

            # Если префабы ничего не вернули, то делаем вызов обработчика команды
            if ban_status[1] is None and authorized_check[1] is None:
                return await func(message, state, get_user_response.json()['user_info'], *args, **kwargs)
        else:
            await state.clear()
            return await message.answer(text=server_error)
    return wrapper


# --- Проверка частоты использования команд --- #
def anti_robot_check(func):
    @wraps(func)
    async def wrapped(message: Message, state: FSMContext, *args, **kwargs):
        if await is_suspected_robot(state):
            return await handle_suspected_robot(message, state)

        return await func(message, state, *args, **kwargs)
    return wrapped

