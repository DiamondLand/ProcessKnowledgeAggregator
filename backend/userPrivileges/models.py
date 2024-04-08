from tortoise import fields
from tortoise.models import Model


# --- Таблица привелегий. Связь с `User` --- #
class UserPrivileges(Model):
    id = fields.IntField(pk=True)

    login = fields.OneToOneField(
        'models.User', to_field='login', on_delete='CASCADE'
    )

    is_admin = fields.BooleanField(default=False)
