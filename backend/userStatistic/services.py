from user.models import User
from .models import UserStatistic
from .schemas import UpdateDataScheme


class StatusService:

    @staticmethod  # Получение статистики
    async def get_statistic_service(user_id: int):
        return await UserStatistic.get_or_none(user_id=user_id)

    @staticmethod  # Обновление количества поинтов
    async def update_points_count_service(data: UpdateDataScheme):
        user = await User.get_or_none(user_id=data.user_id)

        if user:
            response = await UserStatistic.get_or_none(user=data.user_id)

            if response:
                response.points += data.number
                await response.save()
                return {"message": "success"}

    @staticmethod  # Обновление количества поинтов
    async def update_questions_count_service(data: UpdateDataScheme):
        user = await User.get_or_none(user_id=data.user_id)

        if user:
            response = await UserStatistic.get_or_none(user=data.user_id)

            if response:
                response.questions += data.number
                await response.save()
                return {"message": "success"}

    @staticmethod  # Обновление количества поинтов
    async def update_answers_count_service(data: UpdateDataScheme):
        user = await User.get_or_none(user_id=data.user_id)

        if user:
            response = await UserStatistic.get_or_none(user=data.user_id)

            if response:
                response.answers += data.number
                await response.save()
                return {"message": "success"}
