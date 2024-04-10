from userStatistic.models import UserStatistic
from userPrivileges.models import UserPrivileges
from .models import User, BlackList, UserSubsribes
from .schemas import CreateUserScheme, AddToBlackListScheme, ChangeStatusScheme, AuthorizationUserScheme, SubsctribeTagScheme


class UserService:

    @staticmethod  # Получение пользователя
    async def get_user_service(user_id: int):
        user = await User.get_or_none(user_id=user_id)
        subscribes_entries = await UserSubsribes.filter(login=user.login if user else None).all()
        statistic_entry = await UserStatistic.get_or_none(login=user.login if user else None)
        privileges_entry = await UserPrivileges.get_or_none(login=user.login if user else None)
        blacklist_entry = await BlackList.get_or_none(login=user.login if user else None)
        return {
            "user_info": user,
            "user_subsribes": subscribes_entries,
            "user_statistic": statistic_entry,
            "user_privileges": privileges_entry,
            "blacklist_info": blacklist_entry
        }

    @staticmethod  # Получение пользователя по логину
    async def get_account_service(login: str, password: str):
        user = await User.get_or_none(login=login, password=password)
        subscribes_entries = await UserSubsribes.filter(login=user.login if user else None).all()
        statistic_entry = await UserStatistic.get_or_none(login=user.login if user else None)
        privileges_entry = await UserPrivileges.get_or_none(login=user.login if user else None)
        blacklist_entry = await BlackList.get_or_none(login=user.login if user else None)
        return {
            "user_info": user,
            "user_subsribes": subscribes_entries,
            "user_statistic": statistic_entry,
            "user_privileges": privileges_entry,
            "blacklist_info": blacklist_entry
        }

    @staticmethod  # Регистрация пользователя
    async def create_user_service(data: CreateUserScheme):
        check_contacts_response = await User.filter(contacts=data.contacts).exclude(login=data.login).get_or_none()
        check_login_response = await User.filter(login=data.login).exclude(login=data.login).get_or_none()
        another_accounts_response = await User.filter(user_id=data.user_id).all()

        if check_contacts_response is None and check_login_response is None:
            # Отключаемся от других аккаунтов
            if another_accounts_response:
                for account in another_accounts_response:
                    account.user_id = None
                    await account.save()

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

    @staticmethod
    async def authorization_user_service(data: AuthorizationUserScheme):
        check_user_response = await User.get_or_none(login=data.login, password=data.password)
        another_accounts_response = await User.filter(user_id=data.user_id).all()

        # Отключаемся от других аккаунтов
        if another_accounts_response:
            for account in another_accounts_response:
                account.user_id = None
                await account.save()

        if check_user_response:
            check_user_response.user_id = data.user_id
            await check_user_response.save()
            return check_user_response

    @staticmethod  # Подписка на тег
    async def subscribe_tag_service(data: SubsctribeTagScheme):
        user = await User.get_or_none(login=data.login)

        if user:
            response = await UserSubsribes.filter(login=user, tag=data.tag).first()

            if response is None:
                return await UserSubsribes.create(login=user, tag=data.tag)
            else:
                return {'message': 'already subscribe'}

    @staticmethod  # Отпписка от тега
    async def unsubscribe_tag_service(login: str, tag: str):
        user = await User.get_or_none(login=login)

        if user:
            response = await UserSubsribes.filter(login=user.login, tag=tag).first()

            if response:
                await response.delete()
                return {'message': 'success'}

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
