import httpx

from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from functions.card_to_send import send_question_card, send_answer_card
from functions.redis_votes import set_vote, vote_exists, remove_vote

from elements.keyboards.keyboards_profile import profile_kb
from elements.keyboards.keyboards_searching import admin_tape_kb

from elements.answers import server_error

from events.states_group import Searching, CreateAnswer, EditQuestionOrAnswer

from .queue import change_queue_index, get_last_user_id


async def send_moder_tape(state: FSMContext, my_response, message: Message = None, callback: CallbackQuery = None, set_index: bool = True, questions: bool = True, answers: bool = False):
    msg = message or callback
    message_to_send = message or callback.message
    
    async with httpx.AsyncClient() as client:
        get_all_moder_questions_response = await client.get(
            f"{msg.bot.config['SETTINGS']['backend_url']}get_all_moder_questions"
        )

    if get_all_moder_questions_response.status_code == 200:
        get_all_moder_questions_data = get_all_moder_questions_response.json()

        if get_all_moder_questions_data:

            get_index = await complaint_change_queue_index(message=msg, queue=len(all_complaints_data), set_index=False if banned else set_index)

            # Получаем ID последней просмотренной анкеты и обновялем ---
            last_user_id = int(await get_last_user_id(
                message=msg,
                key=f"complaint_last_id_{msg.from_user.id}",
                last_id=all_complaints_data[get_index]['violator_user_id']
            ))
            # Если баним
            if banned is True:
                return await ban_account(message=msg, user_id=last_user_id, state=state)

            # Если `get_index` (ещё есть анкеты для просмотра)
            if get_index >= 0:
                # Получаем данные о user_id
                next_user_response = await check_account(config=msg.bot.config, user_id=all_complaints_data[get_index]['violator_user_id'])
                if next_user_response.status_code == 200:
                    if next_user_response.json():
                        # Отправляем анкету
                        # Отправялем эмодзи и задаём keyboard
                        await message_to_send.answer(
                            text="🔎✨", 
                            reply_markup=complaint_admin_panel_kb()
                        )
                        await send_profile_card(
                            msg=message_to_send,
                            user_id_to_send=msg.from_user.id,
                            user_data_json=next_user_response.json(),
                            caption="<b>⛔ Жалоба на анкету:</b>",
                            is_admin=True
                        )
                    else:
                        # Если анкета не нашлась, то перезаходим в функцию
                        return await send_violator_profile(
                            state=state,
                            message=msg
                        )
                else:
                    return await message_to_send.answer(text=server_error)

            else:
                await state.clear()
                # Очищаем все жалобы
                async with httpx.AsyncClient() as client:
                    delete_complaints_response = await client.delete(
                        f"{msg.bot.config['SETTINGS']['backend_url']}delete_complaints"
                    )
                if delete_complaints_response.status_code != 200:
                    await state.clear()
                    await message_to_send.answer(text="💔 Упс!", reply_markup=ReplyKeyboardRemove())
                    await message_to_send.answer(text=server_error, reply_markup=admin_panel().as_markup())
                
                await message_to_send.answer(text="😉👉🎉", reply_markup=ReplyKeyboardRemove())
                await message_to_send.answer(text="На этом пока что всё ✨", reply_markup=admin_panel().as_markup())
                # --- Отправка сообщения в логи --- #
                await message.bot.send_message(
                    chat_id=message.bot.log_channel,
                    text=f"📕✅ Жалобы рассмотрены администратором <code>{message.from_user.id}</code> (@{message.from_user.username})!"
                )
        else:
            await state.clear()
            await message_to_send.answer(text="🎉", reply_markup=ReplyKeyboardRemove())
            await message_to_send.answer(text="Жалоб пока что нет 😉", reply_markup=admin_panel().as_markup())
    else:
        await state.clear()
        await message_to_send.answer(text="💔 Упс!", reply_markup=ReplyKeyboardRemove())
        await message_to_send.answer(text=server_error, reply_markup=admin_panel().as_markup())
    
