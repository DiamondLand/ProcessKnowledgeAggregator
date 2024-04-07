import httpx


# --- Проверка аккаунта --- #
async def check_account(config, user_id: int):
    async with httpx.AsyncClient() as client:
        return await client.get(
            f"{config['SETTINGS']['backend_url']}get_user?user_id={user_id}"
        )
