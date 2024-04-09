import aioredis

from aiogram.types import Message


async def set_vote(message: Message, key: str) -> int:
    async with aioredis.from_url(message.bot.config["SETTINGS"]["redis"]) as redis:
        response = await redis.set(key, 1)
    return response


async def remove_vote(message: Message, key: str) -> int:
    async with aioredis.from_url(message.bot.config["SETTINGS"]["redis"]) as redis:
        response = await redis.delete(key)
    return response


async def vote_exists(message: Message, key: str) -> int:
    async with aioredis.from_url(message.bot.config["SETTINGS"]["redis"]) as redis:
        response = await redis.exists(key)
    return response