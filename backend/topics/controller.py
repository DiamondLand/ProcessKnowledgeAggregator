from fastapi import APIRouter

from .schemas import *
from .services import TopicService

router = APIRouter()


# --- Получение вопроса --- #
@router.get('/get_question')
async def get_question_controller(question_id: int):
    return await TopicService.get_question_service(question_id=question_id)


# --- Получение вопросов по тегам --- #
@router.get('/get_tag_questions')
async def get_tag_questions_controller(tag: str):
    return await TopicService.get_tag_questions_service(tag=tag)


# --- Получение всех вопросов --- #
@router.get('/get_all_questions')
async def get_all_questions_controller():
    return await TopicService.get_all_questions_service()


# --- Получение всех вопросов пользователя --- #
@router.get('/get_all_user_questions')
async def get_all_user_questions_controller(login: str):
    return await TopicService.get_all_user_questions_service(login=login)


# --- Получение всех ответов пользователя --- #
@router.get('/get_all_user_answers')
async def get_all_user_answers_controller(login: str):
    return await TopicService.get_all_user_answers_service(login=login)


# --- Получение всех отвтов на вопрос --- #
@router.get('/get_all_question_answers')
async def get_all_question_answers_controller(question_id: int):
    return await TopicService.get_all_question_answers_service(question_id=question_id)


# --- Создание вопроса --- #
@router.post('/create_question')
async def create_question_controller(data: CreateQuestion):
    return await TopicService.create_question_service(data=data)


# --- Обновление вопроса --- #
@router.put('/update_question')
async def update_question_controller(data: UpdateQuestion):
    return await TopicService.update_question_service(data=data)


# --- Создание ответа --- #
@router.post('/create_answer')
async def create_answer_controller(data: CreateAnswer):
    return await TopicService.create_answer_service(data=data)


# --- Обновление количества голосов за вопрос --- #
@router.put('/update_question_votes')
async def update_question_votes_controller(data: UpdateVotes):
    return await TopicService.update_question_votes_service(data=data)


# --- Обновление количества голосов за ответ --- #
@router.put('/update_answer_votes')
async def update_answer_votes_controller(data: UpdateVotes):
    return await TopicService.update_answer_votes_service(data=data)


# --- Обновление статуса вопроса --- #
@router.put('/update_question_status')
async def update_question_status_controller(data: UpdateStatus):
    return await TopicService.update_question_status_service(data=data)


# --- Обновление статуса ответа --- #
@router.put('/update_answers_status')
async def update_answers_status_controller(data: UpdateStatus):
    return await TopicService.update_answers_status_service(data=data)


# --- Удаление вопроса --- #
@router.delete('/delete_question')
async def delete_question_controller(question_id: int):
    return await TopicService.delete_question_service(question_id=question_id)


# --- Удаление ответа --- #
@router.delete('/delete_answer')
async def delete_answer_controller(answer_id: int):
    return await TopicService.delete_answer_service(answer_id=answer_id)
