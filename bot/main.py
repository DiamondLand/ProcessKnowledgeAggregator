import configparser
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage

from loguru import logger

from events import errors_handler, profile_events
from handlers.commands import commands_handler
from handlers.register import register, authorization
from handlers.topics.questions import tape_searching, tape_questions
from handlers import different_types

config = configparser.ConfigParser()
config.read("config.ini")

bot = Bot(config["SETTINGS"]["token"], parse_mode=ParseMode.HTML)
storage = RedisStorage.from_url(config["SETTINGS"]["redis"])
dp = Dispatcher(storage=storage)


async def main():
    bot.config = config
    bot.permanent_ids = [8722788581]

    # Подключение модулей
    logger.info("Loading modules...")

    dp.include_routers(
        # Должна быть первым для получения ошибок со всех роутеров
        errors_handler.router, 

        # Пользовательское
        profile_events.router,
        commands_handler.router,
        register.router,
        authorization.router,
        tape_searching.router,
        tape_questions.router,

        # Должно быть в конце для заполения форм
        different_types.router
    )

    await bot.delete_webhook(drop_pending_updates=True)
    logger.success("Successfully launched")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
