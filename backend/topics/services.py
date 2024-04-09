import random

from user.models import User
from userStatistic.models import UserStatistic
from .models import TopicQuections, TopicAnswers
from .schemas import *


class TopicService:

    @staticmethod  # Получение вопроса
    async def get_question_service(question_id: int):
        return await TopicQuections.get_or_none(id=question_id)

    @staticmethod  # Получение вопросов по тегам
    async def get_tag_questions_service(tag: str):
        return await TopicQuections.filter(tag=tag).order_by('-votes').all()

    @staticmethod  # Получение всех вопросов
    async def get_all_questions_service():
        return await TopicQuections.filter().order_by('-votes').all()

    @staticmethod  # Получение всех вопросов пользователя
    async def get_all_user_questions_service(login: str):
        user = await User.get_or_none(login=login)

        if user:
            return await TopicQuections.filter(login=user).order_by('-votes').all()

    @staticmethod  # Получение всех ответов пользователя
    async def get_all_user_answers_service(login: str):
        user = await User.get_or_none(login=login)

        if user:
            return await TopicAnswers.filter(login=user).order_by('-votes').all()

    @staticmethod  # Получение всех ответов на вопрос
    async def get_all_question_answers_service(question_id: int):
        question = await TopicQuections.get_or_none(id=question_id)

        if question:
            return await TopicAnswers.filter(question=question).order_by('-votes').all()

    @staticmethod  # Создание вопроса
    async def create_question_service(data: CreateQuestion):
        user = await User.get_or_none(login=data.login)

        if user:
            question = await TopicQuections.create(tag=data.tag, question=data.question)
            await user.user_question.add(question)
            return question
    
    @staticmethod  # Обновление вопроса
    async def update_question_service(data: UpdateQuestion):
        question = await TopicQuections.get_or_none(id=data.question_id)
        
        if question:
            question.question = data.question
            question.tag = data.tag
            await question.save()
            
            return question

    @staticmethod  # Создание ответа
    async def create_answer_service(data: CreateAnswer):
        user = await User.get_or_none(login=data.login)
        question = await TopicQuections.get_or_none(id=data.question_id)

        if user and question:
            answer = await TopicAnswers.create(answer=data.answer)
            await question.question_to_answer.add(answer)
            await user.user_answers.add(answer)
            return answer

    @staticmethod  # Обновление ответа
    async def update_answer_service(data: UpdateAnswer):
        answer = await TopicAnswers.get_or_none(id=data.answer_id)
        
        if answer:
            answer.answer = data.answer
            await answer.save()
            
            return answer
        
    @staticmethod  # Обновление количества голосов за вопрос
    async def update_question_votes_service(data: UpdateVotes):
        user = await User.get_or_none(login=data.login)

        if user:
            response = await TopicQuections.get_or_none(id=data.part_id)

            if response:
                response.votes += data.number
                await response.save()

                user_statistic_response = await UserStatistic.get_or_none(login=data.login)
                #! Человек может зафармить поинты проставляя голос и убирая его
                if user_statistic_response and data.number > 0:
                    user_statistic_response.points += random.randint(1, 3)
                    await user_statistic_response.save()

                return {"message": "success"}

    @staticmethod  # Обновление оличества голосов за ответ
    async def update_answer_votes_service(data: UpdateVotes):
        user = await User.get_or_none(login=data.login)
        if user:
            response = await TopicAnswers.get_or_none(id=data.part_id)

            if response:
                response.votes += data.number
                await response.save()

            user_statistic_response = await UserStatistic.get_or_none(login=data.login)

            #! Человек может зафармить поинты проставляя голос и убирая его
            if user_statistic_response and data.number > 0:
                user_statistic_response.points += 1
                await user_statistic_response.save()

            return {"message": "success"}

    @staticmethod  # Обновление статуса вопроса
    async def update_question_status_service(data: UpdateStatus):
        user = await User.get_or_none(login=data.login)

        if user:
            response = await TopicQuections.get_or_none(id=data.part_id)

            if response:
                response.status = data.status
                await response.save()
                return {"message": "success"}

    @staticmethod  # Обновление статуса ответа
    async def update_answers_status_service(data: UpdateStatus):
        user = await User.get_or_none(login=data.login)

        if user:
            response = await TopicAnswers.get_or_none(id=data.part_id)

            if response:
                response.status = data.status
                await response.save()
                return {"message": "success"}

    @staticmethod  # Удаление вопроса
    async def delete_question_service(question_id: int):
        response = await TopicQuections.filter(id=question_id).get_or_none()

        if response:
            await response.delete()
            await response.save()
            return {"message": "success"}

    @staticmethod  # Удаление ответа
    async def delete_answer_service(answer_id: int):
        response = await TopicAnswers.filter(id=answer_id).get_or_none()

        if response:
            await response.delete()
            await response.save()
            return {"message": "success"}
