from fastapi import APIRouter

from .schemas import UpdateStatusScheme
from .services import StatusService

router = APIRouter()


# --- Получение списка админов --- #
@router.get('/get_adminlist')
async def get_adminlist_controller():
    return await StatusService.get_adminlist_service()


# --- Изменение статуса админа --- #
@router.put('/update_admin_status')
async def update_admin_status_controller(data: UpdateStatusScheme):
    return await StatusService.update_admin_status_service(data=data)
