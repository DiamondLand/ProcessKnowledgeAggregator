import httpx

from aiogram import Bot


async def send_tags_on_subscribe(bot: Bot):
    async with httpx.AsyncClient() as client:
        get_users_response = await client.get(
            f"{bot.config['SETTINGS']['backend_url']}get_users"
        )
    # * .json() -> [{'user_info'}: ..., {'user_subsribes'}: ..., {'user_statistic'}: ..., {'user_privileges'}: ..., {'blacklist_info'}: ...]

    if get_users_response.status_code == 200 and get_users_response.json():
        for element in get_users_response.json():

            if element['user_subsribes']:
                for sub in element['user_subsribes']:
                    try:
                        await bot.send_message(
                            chat_id=element['user_info']['user_id'],
                            text=f"<b>😉 Новые вопросы в категории <i>{sub['tag']}</i>!</b>\n\
                                \nПосмотрите, может быть вы знаете ответ!"
                        )
                    except:
                        pass