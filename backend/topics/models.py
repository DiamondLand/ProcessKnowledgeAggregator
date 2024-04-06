from tortoise import fields
from tortoise.models import Model


# --- Таблица вопросов. Связь с `User`--- #
class TopicQuections(Model):
    id = fields.IntField(pk=True)

    user = fields.ForeignKeyField(
        'models.User', to_field='user_id'
    )
    tag = fields.CharField(max_length=300)
    question = fields.TextField()

    votes = fields.IntField(default=0)
    created_at = fields.DatetimeField(auto_now=True)

    status = fields.BooleanField(default=False)


# --- Таблица ответов. Связь с `Quections` и `User` --- #
class TopicAnswers(Model):
    id = fields.IntField(pk=True)

    question = fields.ForeignKeyField(
        'models.TopicQuections', on_delete='CASCADE'
    )
    user = fields.ForeignKeyField(
        'models.User', to_field='user_id'
    )
    answer = fields.TextField()

    votes = fields.IntField(default=0)
    created_at = fields.DatetimeField(auto_now=True)

    status = fields.BooleanField(default=False)
