import httpx


# --- Проверка аккаунта --- #
async def check_account(config, user_id: int):
    async with httpx.AsyncClient() as client:
        return await client.get(
            f"{config['SETTINGS']['backend_url']}get_user?user_id={user_id}"
        )


# --- Проверка аккаунта по логину--- #
async def check_account_login(config, login: str):
    async with httpx.AsyncClient() as client:
        return await client.get(
            f"{config['SETTINGS']['backend_url']}get_login?login={login}"
        )
    

# --- Проверка аккаунта по логину и паролю--- #
async def check_account_login_password(config, login: str, password: str):
    async with httpx.AsyncClient() as client:
        return await client.get(
            f"{config['SETTINGS']['backend_url']}get_account?login={login}&password={password}"
        )
