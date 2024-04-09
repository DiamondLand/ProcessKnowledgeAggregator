import httpx

from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from functions.card_to_send import send_question_card, send_answer_card
from functions.redis_votes import set_vote, vote_exists, remove_vote

from elements.keyboards.keyboards_profile import profile_kb
from elements.keyboards.keyboards_searching import my_questions_kb, all_questions_kb, all_answers_kb, my_answers_kb
from elements.keyboards.keyboards_questions import back_to_global_questions_kb, back_to_my_questions_kb

from elements.answers import server_error

from events.states_group import Searching, EditQuestionOrAnswer

from .queue import change_queue_index, get_last_user_id


# --- Функция отправки вопросов --- #
async def send_searching_questions(message: Message, state: FSMContext, my_response, set_index: bool = True, view_answers: bool = False, tag: str = None,
                                    edit: bool = False, vote: bool = False, create_answer: bool = False, global_tape: bool = True, another_key: str = None):
    async with httpx.AsyncClient() as client:
        if global_tape and tag is None:
            questions_response = await client.get(
                f"{message.bot.config['SETTINGS']['backend_url']}get_all_questions"
            )
        elif tag:
            questions_response = await client.get(
                f"{message.bot.config['SETTINGS']['backend_url']}get_tag_questions?tag={tag}"
            )
        else:
            questions_response = await client.get(
                f"{message.bot.config['SETTINGS']['backend_url']}get_all_user_questions?login={my_response['login']}"
            )

    if questions_response.status_code == 200:
        questions_data = questions_response.json()

        if questions_data:
            my_queue_index_key = f"user:{my_response['login']}:my_queue_index"
            queue_index_key = another_key if another_key and tag else f"user:{my_response['login']}:queue_index"
            
            # Получаем индекс вопроса для показа и обновляем id последнего
            get_index = await change_queue_index(
                message=message,
                queue=len(questions_data),
                key=queue_index_key if global_tape else my_queue_index_key,
                set_index=False if view_answers or create_answer or vote or edit else set_index  # Принудительно не задаём новый индекс если хотим просто поличть last_id
            )

            # Получаем ID последнего просмотренного вопроса и обновялем
            last_question_id = await get_last_user_id(
                message=message,
                key=queue_index_key if global_tape else my_queue_index_key,
                last_id=questions_data[get_index]['id']
            )

            # Переход в ленту просмотра ответов
            if view_answers is True:
                await state.set_state(Searching.tape_answers)

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

            # Ответ на вопрос
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

            # Проголосовать за вопрос
            if vote is True:
                key = f"q_vote:{my_response['login']}:{last_question_id}"

                if await vote_exists(message=message, key=key):
                    await remove_vote(message=message, key=key)
                    await message.answer(text="💙 Голос за вопрос убран!")
                    number = -1
                else:
                    await set_vote(message=message, key=key)
                    await message.answer(text="🤍 Голос за вопрос отдан!")
                    number = 1

                async with httpx.AsyncClient() as client:
                    await client.put(message.bot.config['SETTINGS']['backend_url'] + 'update_question_votes', json={
                        'login': my_response['login'],
                        'part_id': last_question_id,
                        'number': number
                    })

                return await send_searching_questions(
                    message=message,
                    state=state,
                    my_response=my_response,
                    set_index=False
                )

            # Если хотим отредактировать на вопрос
            if edit is True:
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
async def send_searching_answers(message: Message, state: FSMContext, question_id: int, my_response, edit: bool = False, set_index: bool = True,
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

            # Проголосовать за ответ
            if vote is True:
                key = f"a_vote:{my_response['login']}:{last_answer_id}"

                if await vote_exists(message=message, key=key):
                    await remove_vote(message=message, key=key)
                    await message.answer(text="💙 Голос за ответ убран!")
                    number = -1
                else:
                    await set_vote(message=message, key=key)
                    await message.answer(text="🤍 Голос за ответ отдан!")
                    number = 1

                async with httpx.AsyncClient() as client:
                    await client.put(message.bot.config['SETTINGS']['backend_url'] + 'update_answer_votes', json={
                        'login': my_response['login'],
                        'part_id': last_answer_id,
                        'number': number
                    })

                return await send_searching_answers(
                    message=message,
                    state=state,
                    question_id=question_id,
                    my_response=my_response,
                    set_index=False
                )

            # Если хотим отредактировать на вопрос
            if edit is True:
                await state.set_state(EditQuestionOrAnswer.edit_answer)

                data = await state.get_data()
                data['answer_id'] = last_answer_id
                data['question_id'] = question_id
                data['user_response'] = my_response
                await state.update_data(data)

                return await message.answer(
                    text=f"<b>Текущий ответ:</b> <i>{answers_data[get_index]['answer']}</i>\n\nВведите новый вариант:",
                    reply_markup=back_to_my_questions_kb()
                )

            await send_answer_card(
                msg=message, 
                answers_data=answers_data[get_index],
                question=get_question.json()['question'] if get_question else None
            )
        else:  
            # Задаём новую стадию просмотра вопросов
            await state.set_state(Searching.tape_questions)

            # Возвращаемся к просмотру ленты
            await message.answer(
                text="<b>Ответов на вопрос пока что нет 😉!</b>\n\nВы можете оставить его первым!",
                reply_markup=all_questions_kb() if global_tape else my_questions_kb()
            )

            await send_searching_questions(
                message=message,
                state=state,
                my_response=my_response,
                set_index=False,
                global_tape=global_tape
            )
    else:
        await message.answer(text=server_error, reply_markup=profile_kb())
