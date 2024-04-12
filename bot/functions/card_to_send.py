from aiogram.types import Message, FSInputFile

from functions.find_photo import find_photo_in_folder


# --- Отправка картотчки вопроса ---
async def send_question_card(msg: Message, questions_data: dict):
    photo_path = find_photo_in_folder(folder_path="bot/assets/questions", id=questions_data['id'])

    if photo_path:
        return await msg.answer_photo(
            photo=FSInputFile(path=photo_path),
            caption=f"\
                <b>🏷 Тег:</b> <code>{questions_data['tag']}</code> | <b>🎉 Голосов:</b> <code>{questions_data['votes']}</code> | <b>😎 Автор:</b> <code>{questions_data['login_id']}</code>\
                \n\
                \n{questions_data['question']}"
        )
    else:
        return await msg.answer(
            text=f"\
                <b>🏷 Тег:</b> <code>{questions_data['tag']}</code> | <b>🎉 Голосов:</b> <code>{questions_data['votes']}</code> | <b>😎 Автор:</b> <code>{questions_data['login_id']}</code>\
                \n\
                \n{questions_data['question']}"
        )


# --- Отправка картотчки ответа ---
async def send_answer_card(msg: Message, answers_data: dict, question: str = None):
    photo_path = find_photo_in_folder(folder_path="bot/assets/answers", id=answers_data['id'])

    if photo_path:
        return await msg.answer_photo(
            photo=FSInputFile(path=photo_path),
            caption=f"\
                <b>Вопрос:</b> <code>{question}</code> | <b>Ответил:</b> <code>{answers_data['login_id']['login']}</code>\
                \n\n<b>🎉 Голосов:</b> <code>{answers_data['votes']}</code>\
                \n{'Промодерирован' if answers_data['status'] is True else 'Не промодерирован'}\
                \n\
                \n{answers_data['answer']}"
        )
    else:
        return await msg.answer(
            text=f"\
                <b>Вопрос:</b> <code>{question}</code> | <b>Ответил:</b> <code>{answers_data['login_id']['login']}</code>\
                \n\n<b>🎉 Голосов:</b> <code>{answers_data['votes']}</code>\
                \n{'Промодерирован' if answers_data['status'] is True else 'Не промодерирован'}\
                \n\
                \n{answers_data['answer']}"
        )
