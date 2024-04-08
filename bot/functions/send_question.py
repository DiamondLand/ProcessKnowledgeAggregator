from aiogram.types import Message

from datetime import datetime


# --- Отправка картотчки вопроса ---
async def send_question_card(msg: Message, questions_data: dict):
    datetime_obj = datetime.strptime(questions_data['created_at'], '%Y-%m-%dT%H:%M:%S.%f%z')
    formatted_time = datetime_obj.strftime('%d-%m-%Y %H:%M')

    return await msg.answer(
        text=f"\
            <b>🏷 Тег:</b> <code>{questions_data['tag']}</code> | <b>🎉 Голосов:</b> <code>{questions_data['votes']}</code>\
            \n<b>Промодерирован:</b> <code>{formatted_time}</code>\
            \n\
            \n{questions_data['question']}"
    )
