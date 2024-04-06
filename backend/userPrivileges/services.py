from user.models import User
from .models import UserPrivileges
from .schemas import UpdateStatusScheme


class StatusService:

    @staticmethod  # Получение списка админов
    async def get_adminlist_service():
        return [*await UserPrivileges.filter(is_admin=True).all()]

    @staticmethod  # Изменение статуса админа
    async def update_admin_status_service(data: UpdateStatusScheme):
        user = await User.get_or_none(user_id=data.user_id)

        if user:
            response = await UserPrivileges.get_or_none(user=data.user_id)

            if response:
                response.is_admin = data.status
                await response.save()
                return {"message": "success"}
