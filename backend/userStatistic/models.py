from tortoise import fields
from tortoise.models import Model


# --- Таблица статистики. Связь с `User` --- #
class UserStatistic(Model):
    id = fields.IntField(pk=True)

    login = fields.OneToOneField(
        'models.User', to_field='login', on_delete='CASCADE'
    )

    points = fields.IntField(default=0)

    questions = fields.IntField(default=0)
    answers = fields.IntField(default=0)
