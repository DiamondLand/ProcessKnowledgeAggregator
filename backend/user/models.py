from tortoise import fields
from tortoise.models import Model


# --- Таблица пользователей --- #
class User(Model):
    id = fields.IntField(pk=True)
    login = fields.CharField(max_length=300, unique=True)
    
    user_id = fields.IntField()
    contacts = fields.CharField(max_length=50, unique=True)
    password = fields.CharField(max_length=300)

    is_authorized = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now=True)


# --- Таблица чёрного списка --- #
class BlackList(Model):
    id = fields.IntField(pk=True)
    login = fields.CharField(max_length=300, unique=True)

    moderated_at = fields.DatetimeField(auto_now=True)
    reason = fields.CharField(max_length=300)
