import httpx

from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from functions.account.account_responses import check_account_login
from functions.card_to_send import send_question_card, send_answer_card

from elements.inline.inline_admin import admins_btns
from elements.keyboards.keyboards_profile import profile_kb

from elements.answers import server_error

from .queue import additional_change_queue_index, get_last_id


async def send_moder_tape(state: FSMContext, message: Message = None, callback: CallbackQuery = None, set_index: bool = True, 
                          questions: bool = False, answers: bool = False, reject: bool = False, accept: bool = False):
    msg = message or callback
    message_to_send = message or callback.message
    
    async with httpx.AsyncClient() as client:
        if questions is True:
            get_all_moder_response = await client.get(
                f"{msg.bot.config['SETTINGS']['backend_url']}get_all_moder_questions"
            )
        else:
            get_all_moder_response = await client.get(
                f"{msg.bot.config['SETTINGS']['backend_url']}get_all_moder_answers"
            )

    if get_all_moder_response.status_code == 200:
        get_all_moder_data = get_all_moder_response.json()
        if get_all_moder_data:
            
            # Ключи для REDIS
            moder_question_last_id = f"user:{msg.from_user.id}:moder_question_last_id"
            moder_answer_last_id = f"user:{msg.from_user.id}:moder_answer_last_id"

            get_index = await additional_change_queue_index(
                message=msg,
                key=moder_question_last_id if questions is True else moder_answer_last_id,
                queue=len(get_all_moder_data), 
                set_index=set_index
            )

            last_id = await get_last_id(
                message=msg,
                key=moder_question_last_id if questions is True else moder_answer_last_id,
                last_id=get_all_moder_data[get_index]['id']
            )

            # Если отклоняем
            if reject is True:
                async with httpx.AsyncClient() as client:
                    if questions is True:
                        delete_response = await client.delete(
                            f"{msg.bot.config['SETTINGS']['backend_url']}delete_question?question_id={last_id}"
                        )

                        get_user_response = await check_account_login(
                            config=msg.bot.config,
                            login=get_all_moder_data[get_index]['login_id']
                        )
                        # * .json() -> [{'user_info'}: ..., {'user_subsribes'}: ..., {'user_statistic'}: ..., {'user_privileges'}: ..., {'blacklist_info'}: ...]

                        chat_id = get_user_response.json()['user_info']['user_id']
                    else:
                        delete_response = await client.delete(
                            f"{msg.bot.config['SETTINGS']['backend_url']}delete_answer?answer_id={last_id}"
                        )

                        chat_id = get_all_moder_data[get_index]['login_id']['user_id']

                    if delete_response.status_code != 200 or delete_response.json() is None:
                        await message_to_send.answer(text=server_error)

                    try:
                        if questions is True:
                            await msg.bot.send_message(
                                chat_id=chat_id,
                                text=f"❌ Ваш запрос на знание <i>{get_all_moder_data[get_index]['question']}</i> отклонили!"
                            )
                        else:
                            await msg.bot.send_message(
                                chat_id=chat_id,
                                text=f"❌ Ваш ответ <i>{get_all_moder_data[get_index]['answer']}</i> отклонили!"
                            )
                    except:
                        pass
            
            # Если одобряем
            if accept is True:
                async with httpx.AsyncClient() as client:
                    if questions is True:
                        await client.put(msg.bot.config['SETTINGS']['backend_url'] + 'update_question_status', json={
                            'login': get_all_moder_data[get_index]['login_id'] if questions is True else get_all_moder_data[get_index]['login_id']['id'],
                            'part_id': last_id,
                            'status': True
                        })
                        
                        get_user_response = await check_account_login(
                            config=msg.bot.config,
                            login=get_all_moder_data[get_index]['login_id']
                        )
                        # * .json() -> [{'user_info'}: ..., {'user_subsribes'}: ..., {'user_statistic'}: ..., {'user_privileges'}: ..., {'blacklist_info'}: ...]
                        
                        chat_id = get_user_response.json()['user_info']['user_id']
                    else:
                        await client.put(msg.bot.config['SETTINGS']['backend_url'] + 'update_answers_status', json={
                            'login': get_all_moder_data[get_index]['login_id']['login'],
                            'part_id': last_id,
                            'status': True
                        })
                        chat_id = get_all_moder_data[get_index]['login_id']['user_id']

                    try:
                        if questions is True:
                            await msg.bot.send_message(
                                chat_id=chat_id,
                                text=f"✅ Ваш запрос на знание <i>{get_all_moder_data[get_index]['question']}</i> одобрен и опубликован!"
                            )
                        else:
                            await msg.bot.send_message(
                                chat_id=chat_id,
                                text=f"✅ Ваш ответ <i>{get_all_moder_data[get_index]['answer']}</i> одобрен и опубликован!"
                            )
                    except:
                        pass

            if get_index >= 0:
                if questions is True:
                    await send_question_card(
                        msg=message_to_send,
                        questions_data=get_all_moder_data[get_index]
                    )
                else:
                    if get_all_moder_data:
                        question_id = get_all_moder_data[get_index]['question_id']['id']

                    if get_all_moder_response.status_code == 200:
                        async with httpx.AsyncClient() as client:
                            get_question = await client.get(
                                f"{msg.bot.config['SETTINGS']['backend_url']}get_question?question_id={question_id}"
                            )
                    else:
                        return await message_to_send.answer(text=server_error)
            
                    await send_answer_card(
                        msg=message_to_send, 
                        answers_data=get_all_moder_data[get_index],
                        question=get_question.json()['question']
                    )

            else:
                await state.clear()
                await message_to_send.answer("На этом пока что всё ✨", reply_markup=ReplyKeyboardRemove())
                await message_to_send.answer("Вы - администратор", reply_markup=admins_btns().as_markup())
        else:
            await state.clear()
            await message_to_send.answer("Модерация данной категории не требуется ✨", reply_markup=ReplyKeyboardRemove())
            await message_to_send.answer("Вы - администратор", reply_markup=admins_btns().as_markup())
    else:
        await state.clear()
        await message_to_send.answer(text=server_error, reply_markup=profile_kb())
