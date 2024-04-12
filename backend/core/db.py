import configparser

from tortoise.contrib.fastapi import register_tortoise


def init_db(app):
    """config = configparser.ConfigParser()
    config.read("bot/config.ini")"""

    register_tortoise(
        app,
        #db_url=f"postgres://{config['DATABASE']['user']}:{config['DATABASE']['password']}@{config['DATABASE']['host']}:{config['DATABASE']['port']}/{config['DATABASE']['database']}",
        db_url='sqlite://bot/assets/database/database.db',
        modules={'models': [
            'user.models',
            'userStatistic.models',
            'userPrivileges.models',
            'topics.models'
            ]
        },
        generate_schemas=True,
        add_exception_handlers=False,
    )
