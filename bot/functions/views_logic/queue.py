import aioredis

from aiogram.types import Message


# --- Изменение и изменение индекса лент --- #
async def change_queue_index(message: Message, queue: int, key: str, set_index: bool = True) -> int:
    async with aioredis.from_url(message.bot.config["SETTINGS"]["redis"]) as redis:
        values = await redis.lrange(key, 0, 1)
        if values:
            user_index = int(values[0])
        else:
            # Если список пуст, добавляем начальное значение
            await redis.lpush(key, 0)
            return 0

        # Изменяем user_index, если необходимо
        if set_index:
            user_index = (user_index + 1) % queue

        # Если user_index стал больше очереди, задаём ноль
        if user_index >= queue:
            user_index = 0

        # Обновляем значение в Redis
        await redis.lset(key, 0, user_index)

    return user_index


# --- Получение и изменение индексов для просмотра дополнительных лент --- #
async def additional_change_queue_index(message: Message, queue: int, key: str, set_index: bool = True) -> int:
    async with aioredis.from_url(message.bot.config["SETTINGS"]["redis"]) as redis:
        values = await redis.lrange(key, 0, 0)
        if values:
            user_index = int(values[0])
        else:
            # Если список пуст, добавляем начальное значение
            await redis.rpush(key, 0)
            user_index = 0

        # Проверяем, не превышает ли индекс общее количество записей
        if set_index and user_index + 1 > queue - 1:
            await redis.delete(key)
            return -1

        # Если нужно установить индекс, обновляем его
        if set_index:
            user_index += 1
            await redis.lset(key, 0, user_index)

        return user_index


# --- Получение и изменение ID поледнего вопроса в ленте --- #
async def get_last_user_id(message: Message, key: str, last_id: int = None) -> int:
    async with aioredis.from_url(message.bot.config["SETTINGS"]["redis"]) as redis:
        # Получение текущих значений из Redis
        values = await redis.lrange(key, 0, 1)
        if values:
            last_user_id = int(values[1]) if len(values) > 1 else 0
            # Если last_id задан, обновляем last_user_id
            if last_id:

                if len(values) < 2:  # Если нет второго элемента
                    await redis.rpush(key, last_user_id)

                await redis.lset(key, 1, last_id)
            
            return last_user_id
        else:
            return last_id

