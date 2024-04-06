from userStatistic.models import UserStatistic
from userPrivileges.models import UserPrivileges
from .models import User, BlackList
from .schemas import CreateUserScheme, AddToBlackListScheme



class UserService:

    @staticmethod  # Получение пользователя
    async def get_user_service(user_id: int):
        user = await User.get_or_none(user_id=user_id)
        statistic_entry = await UserStatistic.get_or_none(user_id=user_id)
        privileges_entry = await UserPrivileges.get_or_none(user_id=user_id)
        blacklist_entry = await BlackList.get_or_none(user_id=user_id)
        return {
            "user_info": user,
            "user_statistic": statistic_entry,
            "user_privileges": privileges_entry,
            "blacklist_info": blacklist_entry
        }

    @staticmethod  # Регистрация пользователя
    async def create_user_service(data: CreateUserScheme):
        check_phone_response = await User.filter(phone=data.phone).exclude(user_id=data.user_id).get_or_none()
        check_login_response = await User.filter(login=data.login).exclude(user_id=data.user_id).get_or_none()

        if check_phone_response is None and check_login_response is None:
            user, created = await User.update_or_create(
                user_id=data.user_id,
                defaults={
                    'phone': data.phone,
                    'login': data.login,
                    'password': data.password
                }
            )

            # Если пользователь создан, создаем новые связи
            if created:
                await UserStatistic.create(user=user)
                await UserPrivileges.create(user=user)

            return user

    @staticmethod  # Удаление пользователя
    async def delete_user_service(user_id: int):
        user = await User.get_or_none(user_id=user_id)

        if user:
            await user.delete()  # Удаление свзяанных таблиц автоматическое
            return {"message": "success"}

    @staticmethod  # Получение данных о чёрном списке
    async def get_blacklist_service():
        return await BlackList.filter().all()

    @staticmethod  # Занесение в чёрный список
    async def add_to_blacklist_service(data: AddToBlackListScheme):
        return await BlackList.update_or_create(
            user_id=data.user_id,
            defaults={
                'reason': data.reason
            }
        )

    @staticmethod  # Удаление пользователя из чёрного списка
    async def delete_from_blacklist_service(user_id: int):
        blacklist = await BlackList.filter(user_id=user_id).get_or_none()

        if blacklist:
            await blacklist.delete()
            return {'message': 'success'}
