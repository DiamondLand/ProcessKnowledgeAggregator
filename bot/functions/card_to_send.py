from aiogram.types import Message


# --- Отправка картотчки вопроса ---
async def send_question_card(msg: Message, questions_data: dict):
    return await msg.answer(
        text=f"\
            <b>🏷 Тег:</b> <code>{questions_data['tag']}</code> | <b>🎉 Голосов:</b> <code>{questions_data['votes']}</code> | <b>😎 Автор:</b> <code>{questions_data['login_id']}</code>\
            \n\
            \n{questions_data['question']}"
    )


# --- Отправка картотчки ответа ---
async def send_answer_card(msg: Message, answers_data: dict, question: str = None):
    return await msg.answer(
        text=f"\
            <b>Вопрос:</b> {question}\
            \n\n<b>🎉 Голосов:</b> <code>{answers_data['votes']}</code>\
            \n\
            \n{answers_data['answer']}"
    )
