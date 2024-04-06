import random

from user.models import User
from userStatistic.models import UserStatistic
from .models import TopicQuections, TopicAnswers
from .schemas import *


class TopicService:

    @staticmethod  # Получение вопроса
    async def get_question_service(question_id: int):
        return await TopicQuections.get_or_none(id=question_id)

    @staticmethod  # Получение всех вопросов
    async def get_all_questions_service():
        return await TopicQuections.filter().all()

    @staticmethod  # Получение всех вопросов пользователя
    async def get_all_user_questions_service(user_id: int):
        return await TopicQuections.filter(user_id=user_id).all()

    @staticmethod  # Получение всех ответов пользователя
    async def get_all_user_answers_service(user_id: int):
        return await TopicAnswers.filter(user_id=user_id).all()

    @staticmethod  # Получение всех ответов на вопрос
    async def get_all_question_answers_service(question_id: int):
        return await TopicAnswers.filter(question_id=question_id).all()

    @staticmethod  # Создание вопроса
    async def create_question_service(data: CreateQuestion):
        question, _created = await TopicQuections.update_or_create(
            user_id=data.user_id,
            defaults={
                'tag': data.tag,
                'question': data.question
            }
        )

        return question

    @staticmethod  # Создание ответа
    async def create_answer_service(data: CreateAnswer):
        answer, _created = await TopicAnswers.update_or_create(
            user_id=data.user_id,
            question_id=data.question_id,
            defaults={
                'answer': data.answer
            }
        )

        return answer

    @staticmethod  # Обновление количества голосов за вопрос
    async def update_question_votes_service(data: UpdateVotes):
        response = await TopicQuections.get_or_none(id=data.part_id)

        if response:
            response.votes += data.number
            await response.save()

            user_statistic_response = await UserStatistic.get_or_none(user_id=data.user_id)
            # ! Человек может зафармить поинты проставляя голос и убирая его
            if user_statistic_response and data.number > 0:
                user_statistic_response.points += random.randint(1, 3)
                await user_statistic_response.save()

    @staticmethod  # Обновление оличества голосов за ответ
    async def update_answers_votes_service(data: UpdateVotes):
        response = await TopicAnswers.get_or_none(question_id=data.part_id)

        if response:
            response.votes += data.number
            await response.save()

        user_statistic_response = await UserStatistic.get_or_none(user_id=data.user_id)

        # ! Человек может зафармить поинты проставляя голос и убирая его
        if user_statistic_response and data.number > 0:
            user_statistic_response.points += 1
            await user_statistic_response.save()

    @staticmethod  # Обновление статуса вопроса
    async def update_question_status_service(data: UpdateStatus):
        response = await TopicQuections.get_or_none(id=data.part_id)

        if response:
            response.status = data.status
            await response.save()

            user_statistic_response = await UserStatistic.get_or_none(user_id=data.user_id)
            if user_statistic_response and data.number > 0:
                user_statistic_response.questions += 1
                user_statistic_response.points += random.randint(1, 5)
                await user_statistic_response.save()

    @staticmethod  # Обновление статуса ответа
    async def update_answers_status_service(data: UpdateStatus):
        response = await TopicAnswers.get_or_none(question_id=data.part_id)

        if response:
            response.status = data.status
            await response.save()

            user_statistic_response = await UserStatistic.get_or_none(user_id=data.user_id)
            if user_statistic_response and data.number > 0:
                user_statistic_response.answers += 1
                user_statistic_response.points += random.randint(1, 3)
                await user_statistic_response.save()

    @staticmethod  # Удаление вопроса
    async def delete_question_service(question_id: int):
        response = await TopicQuections.filter(id=question_id).get_or_none()

        if response:
            await response.delete()
            await response.save()
            return {"message": "success"}
    
    @staticmethod  # Удаление ответа
    async def delete_answer_service(question_id: int):
        response = await TopicAnswers.filter(question_id=question_id).get_or_none()

        if response:
            await response.delete()
            await response.save()
            return {"message": "success"}
