from fastapi import APIRouter

from .schemas import UpdateDataScheme
from .services import StatusService

router = APIRouter()


# --- Получение статистики --- #
@router.get('/get_statistic')
async def get_statistic_controller(user_id: int):
    return await StatusService.get_statistic_service(user_id=user_id)


# --- Обновление количества поинтов --- #
@router.put('/update_points_count')
async def update_points_count_controller(data: UpdateDataScheme):
    return await StatusService.update_points_count_service(data=data)


# --- Обновление количества вопросов --- #
@router.put('/update_questions_count')
async def update_questions_count_controller(data: UpdateDataScheme):
    return await StatusService.update_questions_count_service(data=data)


# --- Обновление количества ответов --- #
@router.put('/update_answers_count')
async def update_answers_count_controller(data: UpdateDataScheme):
    return await StatusService.update_answers_count_service(data=data)
