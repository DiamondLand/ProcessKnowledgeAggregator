from tortoise import fields
from tortoise.models import Model


# --- Таблица пользователей --- #
class User(Model):
    id = fields.IntField(pk=True)
    user_id = fields.BigIntField(unique=True)

    contacts = fields.CharField(max_length=50, unique=True)
    login = fields.CharField(max_length=300, unique=True)
    password = fields.CharField(max_length=300)

    created_at = fields.DatetimeField(auto_now=True)


# --- Таблица чёрного списка --- #
class BlackList(Model):
    id = fields.IntField(pk=True)
    user_id = fields.BigIntField(unique=True)

    moderated_at = fields.DatetimeField(auto_now=True)
    reason = fields.CharField(max_length=300)
