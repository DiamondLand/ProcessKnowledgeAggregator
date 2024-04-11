import configparser
import asyncio
import aioschedule

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage

from loguru import logger

from functions.account.account_send_sub_questions import send_tags_on_subscribe

from events import errors_handler, profile_events
from handlers.commands import commands_handler
from handlers.admin.blacklist import add_to_blacklist, get_blacklist, remove_from_blacklist
from handlers.register import register, authorization
from handlers.topics.questions import tape_start_searching, create_question, create_answers, tape_questions
from handlers import different_types

config = configparser.ConfigParser()
config.read("config.ini")

bot = Bot(config["SETTINGS"]["token"], parse_mode=ParseMode.HTML)
storage = RedisStorage.from_url(config["SETTINGS"]["redis"])
dp = Dispatcher(storage=storage)


async def main():
    bot.config = config
    bot.permanent_ids = [872278858]

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
        tape_start_searching.router,
        tape_questions.router,
        create_question.router,
        create_answers.router,

        # Админское
        add_to_blacklist.router,
        get_blacklist.router,
        remove_from_blacklist.router,

        # Должно быть в конце для заполения форм
        different_types.router
    ) 

    #await send_tags_on_subscribe(bot=bot)
    await bot.delete_webhook(drop_pending_updates=True)
    logger.success("Successfully launched")
    await dp.start_polling(bot)


async def scheduler():
    aioschedule.every().day.at("10:00").do(send_tags_on_subscribe, bot)

    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def run_both():
    tasks = [asyncio.create_task(scheduler()), asyncio.create_task(main())]
    await asyncio.wait(tasks)


if __name__ == "__main__":
    asyncio.run(run_both())
