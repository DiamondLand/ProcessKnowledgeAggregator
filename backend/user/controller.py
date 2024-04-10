from fastapi import APIRouter

from .schemas import CreateUserScheme, AddToBlackListScheme, ChangeStatusScheme, AuthorizationUserScheme, SubsctribeTagScheme
from .services import UserService


router = APIRouter()


# --- Получение пользователя --- #
@router.get('/get_user')
async def get_user_controller(user_id: int):
    return await UserService.get_user_service(user_id=user_id)


# --- Получение пользователя по логину --- #
@router.get('/get_account')
async def get_account_controller(login: str, password: str):
    return await UserService.get_account_service(login=login, password=password)


# --- Регистрация пользователя --- #
@router.post('/create_user')
async def create_user_controller(data: CreateUserScheme):
    return await UserService.create_user_service(data=data)


# --- Авторизация пользователя --- #
@router.put('/authorization_user')
async def authorization_user_controller(data: AuthorizationUserScheme):
    return await UserService.authorization_user_service(data=data)


# --- Подписка на тег --- #
@router.post('/subscribe_tag')
async def subscribe_tag_controller(data: SubsctribeTagScheme):
    return await UserService.subscribe_tag_service(data=data)


# --- Отписка от тега --- #
@router.delete('/unsubscribe_tag')
async def unsubscribe_tag_controller(login: str, tag: str):
    return await UserService.unsubscribe_tag_service(login=login, tag=tag)


# --- Удаление пользователя --- #
@router.delete('/delete_user')
async def delete_account_controller(login: str):
    return await UserService.delete_user_service(login=login)


# --- Изменение статуса авторизации --- #
@router.put('/change_authorized_status')
async def change_authorized_status_controller(data: ChangeStatusScheme):
    return await UserService.change_authorized_status_service(data=data)


# --- Получение данных о чёрном списке --- #
@router.get('/get_blacklist')
async def get_blacklist_controller():
    return await UserService.get_blacklist_service()


# --- Занесение в чёрный список --- #
@router.post('/add_to_blacklist')
async def add_to_blacklist_controller(data: AddToBlackListScheme):
    return await UserService.add_to_blacklist_service(data=data)


# --- Удаление из чёрного списока --- #
@router.delete('/delete_from_blacklist')
async def delete_from_blacklist_controller(login: str):
    return await UserService.delete_from_blacklist_service(login=login)
