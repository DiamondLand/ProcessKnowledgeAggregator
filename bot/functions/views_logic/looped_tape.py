import httpx

from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from functions.card_to_send import send_question_card, send_answer_card

from elements.keyboards.keyboards_profile import profile_kb
from elements.keyboards.keyboards_searching import all_answers_kb, my_answers_kb
from elements.keyboards.keyboards_questions import back_to_global_questions_kb, back_to_my_questions_kb

from elements.answers import server_error

from events.states_group import Searching, EditQuestionOrAnswer

from .queue import change_queue_index, get_last_user_id


# --- Функция отправки вопросов --- #
async def send_searching_questions(message: Message, state: FSMContext, my_response, set_index: bool = True, view_answers: bool = False,
                                    edit_question: bool = False, create_answer: bool = False, global_tape: bool = True):
    async with httpx.AsyncClient() as client:
        if global_tape:
            questions_response = await client.get(
                f"{message.bot.config['SETTINGS']['backend_url']}get_all_questions"
            )
        else:
            questions_response = await client.get(
                f"{message.bot.config['SETTINGS']['backend_url']}get_all_user_questions?login={my_response['login']}"
            )

    if questions_response.status_code == 200:
        questions_data = questions_response.json()

        if questions_data:
            my_queue_index_key = f"user:{message.from_user.id}:my_queue_index"
            queue_index_key = f"user:{message.from_user.id}:queue_index"
            
            # Получаем индекс вопроса для показа и обновляем id последнего
            get_index = await change_queue_index(
                message=message,
                queue=len(questions_data),
                key=queue_index_key if global_tape else my_queue_index_key,
                set_index=False if create_answer or edit_question or view_answers else set_index  # Принудительно не задаём новый индекс если хотим просто поличть last_id
            )

            # Получаем ID последнего просмотренного вопроса и обновялем
            last_question_id = await get_last_user_id(
                message=message,
                key=queue_index_key if global_tape else my_queue_index_key,
                last_id=questions_data[get_index]['id']
            )
            
            # Переход в ленту просмотра ответов
            if view_answers is True:
                await state.set_state(Searching.view_answers)

                data = await state.get_data()
                data['question_id'] = last_question_id
                data['user_response'] = my_response
                data['global_tape'] = global_tape
                await state.update_data(data)

                await message.answer(
                    text="✨🔎",
                    reply_markup=all_answers_kb() if global_tape else my_answers_kb()
                )

                return await send_searching_answers(
                    message=message,
                    state=state,
                    question_id=last_question_id,
                    my_response=my_response,
                    global_tape=global_tape
                )
            
            # :TODO: Если хотим ответить на вопрос
            if create_answer is True:
                await state.set_state(Searching.create_answer)

                data = await state.get_data()
                data['question_id'] = last_question_id
                data['user_response'] = my_response
                await state.update_data(data)

                return await message.answer(
                    text=f"Напишите ответ для вопроса <i>{questions_data[get_index]['question']}</i> или прикрепите фотографию:",
                    reply_markup=back_to_global_questions_kb() if global_tape else back_to_my_questions_kb()
                )

            # :TODO: Если хотим отредактировать на вопрос
            if edit_question is True:
                await state.set_state(EditQuestionOrAnswer.edit_question)

                data = await state.get_data()
                data['question_id'] = last_question_id
                data['user_response'] = my_response
                await state.update_data(data)

                return await message.answer(
                    text=f"<b>Текущий вопрос:</b> <i>{questions_data[get_index]['question']}</i>\n\nВведите новый вариант:",
                    reply_markup=back_to_my_questions_kb()
                )

            await send_question_card(
                msg=message,
                questions_data=questions_data[get_index]
            )
        else:
            await message.answer(text="<b>Заданных вопросов пока что нет 😉!</b>\n\nВы можете создать первый.", reply_markup=profile_kb())
    else:
        await message.answer(text=server_error, reply_markup=profile_kb())


# --- Функция отправки ответов --- #
async def send_searching_answers(message: Message, state: FSMContext, question_id: int, my_response, set_index: bool = True,
                                vote: bool = False, global_tape: bool = True):
    get_question = None
    async with httpx.AsyncClient() as client:
        if global_tape:
            get_question = await client.get(
                f"{message.bot.config['SETTINGS']['backend_url']}get_question?question_id={question_id}"
            )
            answers_response = await client.get(
                f"{message.bot.config['SETTINGS']['backend_url']}get_all_question_answers?question_id={question_id}"
            )
        else:
            answers_response = await client.get(
                f"{message.bot.config['SETTINGS']['backend_url']}get_all_user_answers?login={my_response['login']}"
            )

    if answers_response.status_code == 200:
        answers_data = answers_response.json()

        if answers_data:
            my_answers_queue_index_key = f"user:{message.from_user.id}:my_answers_queue_index"
            answers_queue_index_key = f"user:{message.from_user.id}:answers_queue_index"
            # Получаем индекс вопроса для показа и обновляем id последнего
            get_index = await change_queue_index(
                message=message,
                queue=len(answers_data),
                key=answers_queue_index_key if global_tape else my_answers_queue_index_key,
                set_index=False if vote else set_index  # Принудительно не задаём новый индекс если хотим просто поличть last_id
            )
            # Получаем ID последнего просмотренного ответа и обновялем
            last_answer_id = await get_last_user_id(
                message=message,
                key=answers_queue_index_key if global_tape else my_answers_queue_index_key,
                last_id=answers_data[get_index]['id']
            )

            # :TODO: Если хотим отдать голос вопросу
            if vote is True:
                ...

            await send_answer_card(
                msg=message, 
                answers_data=answers_data[get_index],
                question=get_question.json()['question'] if get_question else None
            )
        else:
            await message.answer(text="<b>Ответов на вопрос пока что нет 😉!</b>\n\nВы можете дать первый.", reply_markup=profile_kb())
    else:
        await message.answer(text=server_error, reply_markup=profile_kb())
