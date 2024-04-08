from tortoise import fields
from tortoise.models import Model


# --- Таблица вопросов. Связь с `User`--- #
class TopicQuections(Model):
    id = fields.IntField(pk=True)

    login = fields.ManyToManyField(
        'models.User', related_name='user_question', 
        to_field='login'
    )
    tag = fields.CharField(max_length=300)
    question = fields.TextField()

    votes = fields.IntField(default=0)
    created_at = fields.DatetimeField(auto_now=True)

    status = fields.BooleanField(default=False)


# --- Таблица ответов. Связь с `Quections` и `User` --- #
class TopicAnswers(Model):
    id = fields.IntField(pk=True)

    question = fields.ManyToManyField(
        'models.TopicQuections', 
        related_name='question_to_answer', on_delete='CASCADE'
    )
    login = fields.ManyToManyField(
        'models.User', 
        related_name='user_answers', to_field='login'
    )
    answer = fields.TextField()

    votes = fields.IntField(default=0)
    created_at = fields.DatetimeField(auto_now=True)

    status = fields.BooleanField(default=False)
