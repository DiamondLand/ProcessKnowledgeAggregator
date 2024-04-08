from userStatistic.models import UserStatistic
from userPrivileges.models import UserPrivileges
from .models import User, BlackList
from .schemas import CreateUserScheme, AddToBlackListScheme, ChangeStatusScheme


class UserService:

    @staticmethod  # Получение пользователя
    async def get_user_service(user_id: int):
        user = await User.get_or_none(user_id=user_id)
        statistic_entry = await UserStatistic.get_or_none(login=user.login if user else None)
        privileges_entry = await UserPrivileges.get_or_none(login=user.login if user else None)
        blacklist_entry = await BlackList.get_or_none(login=user.login if user else None)
        return {
            "user_info": user,
            "user_statistic": statistic_entry,
            "user_privileges": privileges_entry,
            "blacklist_info": blacklist_entry
        }

    @staticmethod  # Регистрация пользователя
    async def create_user_service(data: CreateUserScheme):
        check_contacts_response = await User.filter(contacts=data.contacts).exclude(login=data.login).get_or_none()

        if check_contacts_response is None:
            user, created = await User.update_or_create(
                login=data.login,
                defaults={
                    'user_id': data.user_id,
                    'contacts': data.contacts,
                    'password': data.password
                }
            )

            # Если пользователь создан, создаем новые связи
            if created:
                await UserStatistic.create(login=user)
                await UserPrivileges.create(login=user)

            return user

    @staticmethod  # Удаление пользователя
    async def delete_user_service(login: str):
        user = await User.get_or_none(login=login)

        if user:
            await user.delete()  # Удаление свзяанных таблиц автоматическое
            return {"message": "success"}

    @staticmethod  # Изменение статуса авторизации
    async def change_authorized_status_service(data: ChangeStatusScheme):
        user = await User.get_or_none(login=data.login)

        if user:
            user.is_authorized += data.status
            await user.save()
            return {"message": "success"}

    @staticmethod  # Получение данных о чёрном списке
    async def get_blacklist_service():
        return await BlackList.filter().all()

    @staticmethod  # Занесение в чёрный список
    async def add_to_blacklist_service(data: AddToBlackListScheme):
        return await BlackList.update_or_create(
            login=data.login,
            defaults={
                'reason': data.reason
            }
        )

    @staticmethod  # Удаление пользователя из чёрного списка
    async def delete_from_blacklist_service(login: str):
        blacklist = await BlackList.filter(login=login).get_or_none()

        if blacklist:
            await blacklist.delete()
            return {'message': 'success'}
