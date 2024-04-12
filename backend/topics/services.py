import random

from user.models import User
from userStatistic.models import UserStatistic
from .models import TopicQuestions,  TopicAnswers
from .schemas import *


class TopicService:

    @staticmethod  # Получение вопроса
    async def get_question_service(question_id: int): 
        return await TopicQuestions.filter(id=question_id).first().prefetch_related('login')

    @staticmethod  # Получение вопросов по тегам
    async def get_tag_questions_service(tag: str):
        return await TopicQuestions.filter(tag=tag, status=True).order_by('-votes').all()

    @staticmethod  # Получение всех вопросов 
    async def get_all_questions_service():
        return await TopicQuestions.filter(status=True).order_by('-votes').all()    
    
    @staticmethod  # Получение всех вопросов на модерации
    async def get_all_moder_questions_service():
        return await TopicQuestions.filter(status=False).order_by('-votes').all()

    @staticmethod  # Получение всех вопросов пользователя
    async def get_all_user_questions_service(login: str):
        user = await User.get_or_none(login=login)

        if user:
            return await TopicQuestions.filter(login_id=user.login).order_by('-votes').all()

    @staticmethod  # Получение всех ответов на модерации
    async def get_all_moder_answers_service():
        responses = await TopicAnswers.filter(status=False).order_by('-votes').all()

        results = []

        for response in responses:
            # Получаем все связанные вопросы для текущего ответа
            related_questions = await response.question.all()

            # Извлекаем ID первого вопроса из связанных вопросов
            if related_questions:
                question_id = related_questions[0]
            else:
                question_id = None

            # Получаем список связанных пользователей
            logins = await response.login.all()

            # Проверяем, есть ли пользователи в списке
            if logins:
                login_id = logins[0]
            else:
                login_id = None

            # Создаем словарь с информацией об ответе и его связанном вопросе
            result_data = {
                'id': response.id,
                'question_id': question_id,
                'login_id': login_id,
                'status': response.status,
                'votes': response.votes,
                'created_at': response.created_at.isoformat(),
                'answer': response.answer
            }

            # Добавляем созданный словарь в список результатов
            results.append(result_data)
        
        return results

    @staticmethod  # Получение всех ответов пользователя
    async def get_all_user_answers_service(login: str):
        user = await User.get_or_none(login=login)

        if user:
            # Получаем все ответы пользователя, отсортированные по количеству голосов
            responses = await TopicAnswers.filter(login=user).order_by('-votes').all()

            # Список для хранения результатов
            results = []

            for response in responses:
                # Получаем все связанные вопросы для текущего ответа
                related_questions = await response.question.all()

                # Извлекаем ID первого вопроса из связанных вопросов
                if related_questions:
                    question_id = related_questions[0].id
                else:
                    question_id = None

                # Получаем список связанных пользователей
                logins = await response.login.all()

                # Проверяем, есть ли пользователи в списке
                if logins:
                    login_id = logins[0]
                else:
                    login_id = None

                # Создаем словарь с информацией об ответе и его связанном вопросе
                result_data = {
                    'id': response.id,
                    'question_id': question_id,
                    'login_id': login_id,
                    'status': response.status,
                    'votes': response.votes,
                    'created_at': response.created_at.isoformat(),
                    'answer': response.answer
                }

                # Добавляем созданный словарь в список результатов
                results.append(result_data)

            return results

    @staticmethod  # Получение всех ответов на вопрос
    async def get_all_question_answers_service(question_id: int):
        question = await TopicQuestions.get_or_none(id=question_id, status=True)

        if question:
            answers = await TopicAnswers.filter(question=question, status=True).order_by('-votes').prefetch_related('login').all()

            # Список для хранения результатов
            results = []

            for answer in answers:
                # Получаем список связанных пользователей
                logins = await answer.login.all()

                # Проверяем, есть ли пользователи в списке
                if logins:
                    login_id = logins[0]
                else:
                    login_id = None

                # Создаем словарь с информацией об ответе и его связанном вопросе
                result_data = {
                    'id': answer.id,
                    'question_id': question_id,
                    'login_id': login_id,
                    'status': answer.status,
                    'votes': answer.votes,
                    'created_at': answer.created_at.isoformat(),
                    'answer': answer.answer
                }

                # Добавляем созданный словарь в список результатов
                results.append(result_data)

            return results

    @staticmethod  # Создание вопроса
    async def create_question_service(data: CreateQuestion):
        user = await User.get_or_none(login=data.login)
        statistic = await UserStatistic.get_or_none(login=data.login)

        if user and statistic:
            question = await TopicQuestions.create(login=user, tag=data.tag, question=data.question)

            statistic.questions += 1
            await statistic.save()

            return question

    @staticmethod  # Обновление вопроса
    async def update_question_service(data: UpdateQuestion):
        question = await TopicQuestions.get_or_none(id=data.question_id)

        if question:
            question.question = data.question
            question.tag = data.tag
            question.status = False
            await question.save()

            return question

    @staticmethod  # Создание ответа
    async def create_answer_service(data: CreateAnswer):
        user = await User.get_or_none(login=data.login)
        statistic = await UserStatistic.get_or_none(login=data.login)
        question = await TopicQuestions.get_or_none(id=data.question_id)

        if user and question and statistic:
            answer = await TopicAnswers.create(answer=data.answer)
            await question.question_to_answer.add(answer)
            await user.user_answers.add(answer)

            statistic.answers += 1
            await statistic.save()

            return answer

    @staticmethod  # Обновление ответа
    async def update_answer_service(data: UpdateAnswer):
        answer = await TopicAnswers.get_or_none(id=data.answer_id)

        if answer:
            answer.answer = data.answer
            answer.status = False
            await answer.save()

            return answer

    @staticmethod  # Изменение подписки на ответы вопроса
    async def subscribe_answers_service(data: UpdateStatus):
        answer = await TopicQuestions.get_or_none(id=data.part_id)

        if answer:
            answer.is_subscribe = data.status
            await answer.save()

            return answer

    @staticmethod  # Обновление количества голосов за вопрос
    async def update_question_votes_service(data: UpdateVotes):
        user = await User.get_or_none(login=data.login)

        if user:
            response = await TopicQuestions.get_or_none(id=data.part_id)

            if response:
                response.votes += data.number
                await response.save()

                user_statistic_response = await UserStatistic.get_or_none(login=data.login)

                if user_statistic_response and data.number > 0:
                    user_statistic_response.points += 1
                    await user_statistic_response.save()
                elif data.number < 0 and user_statistic_response.points >= 1:
                    user_statistic_response.points -= 1
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

            if user_statistic_response and data.number > 0:
                user_statistic_response.points += 1
                await user_statistic_response.save()
            elif data.number < 0 and user_statistic_response.points >= 1:
                user_statistic_response.points -= 1
                await user_statistic_response.save()

            return {"message": "success"}

    @staticmethod  # Обновление статуса вопроса
    async def update_question_status_service(data: UpdateStatus):
        user = await User.get_or_none(login=data.login)

        if user:
            response = await TopicQuestions.get_or_none(id=data.part_id)

            if response:
                response.status = data.status
                await response.save()
            
            user_statistic_response = await UserStatistic.get_or_none(login=data.login)

            if user_statistic_response:
                user_statistic_response.points += 2
                await user_statistic_response.save()

                return {"message": "success"}

    @staticmethod  # Обновление статуса ответа
    async def update_answers_status_service(data: UpdateStatus):
        user = await User.get_or_none(login=data.login)

        if user:
            response = await TopicAnswers.get_or_none(id=data.part_id)

            if response:
                response.status = data.status
                await response.save()
            
            user_statistic_response = await UserStatistic.get_or_none(login=data.login)

            if user_statistic_response:
                user_statistic_response.points += 2
                await user_statistic_response.save()

                return {"message": "success"}

    @staticmethod  # Удаление вопроса
    async def delete_question_service(question_id: int):
        response = await TopicQuestions.filter(id=question_id).get_or_none()

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
