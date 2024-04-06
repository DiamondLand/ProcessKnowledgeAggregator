import aioredis

from aiogram.types import Message
from aiogram.exceptions import TelegramBadRequest


# --- Получение username по id --- #
async def get_account_username(message: Message, user_id: int):
    try:
        chat_info = await message.bot.get_chat(user_id)
        return chat_info.username
    except TelegramBadRequest:
        return user_id


# --- Удаление и данных в redis --- #
async def delete_redis_keys(msg: Message, user_id: int):
    async with aioredis.from_url(msg.bot.config["SETTINGS"]["redis"]) as redis:
        keys = await redis.keys(f"user:{user_id}*")
        await redis.delete(*keys)
