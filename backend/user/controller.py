from fastapi import APIRouter

from .schemas import CreateUserScheme, AddToBlackListScheme, ChangeStatusScheme
from .services import UserService


router = APIRouter()


# --- Получение пользователя --- #
@router.get('/get_user')
async def get_user_controller(login: str):
    return await UserService.get_user_service(login=login)


# --- Регистрация пользователя --- #
@router.post('/create_user')
async def create_user_controller(data: CreateUserScheme):
    return await UserService.create_user_service(data=data)


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
