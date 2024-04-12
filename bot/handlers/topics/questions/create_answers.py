import httpx
import random
import string
import re

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext

from decorators.profile_decorator import anti_robot_check

from functions.find_photo import find_photo_in_folder
from functions.inline_remove import remove_button
from functions.views_logic.looped_tape import send_searching_answers
from functions.account.account_responses import check_account_login

from elements.inline.inline_profile import finish_answers_btns
from elements.keyboards.keyboards_searching import all_answers_kb, my_answers_kb
from elements.keyboards.keyboards_profile import profile_kb

from elements.keyboards.text_on_kb import next_my_answer, next_all_answer, vote_answer, edit_my_answer

from elements.answers import no_state, server_error

from events.states_group import Searching, EditQuestionOrAnswer, CreateAnswer

router = Router()


# --- Кнопки действий при просмотре ленты ответов на вопрос --- #
@router.message(
    Searching.tape_answers,
    (F.text == next_my_answer) | (F.text == next_all_answer) | (F.text == vote_answer) | (F.text == edit_my_answer)
)
@anti_robot_check
async def profile_searching(message: Message, state: FSMContext):
    data = await state.get_data()

    if not data:
        await state.clear()
        return await message.answer(text=no_state, reply_markup=profile_kb())
    
    my_response = data.get('user_response', None)
    global_tape = data.get('global_tape', True)
    question_id = data.get('question_id', None)
    
    actions = {
        'vote': message.text in [vote_answer],
        'edit': message.text in [edit_my_answer],
        'global_tape': global_tape
    }

    # Переходим в функцию просмотра ленты с дополнительными параметрами
    await send_searching_answers(
        message=message,
        state=state,
        question_id=question_id,
        my_response=my_response,
        **actions
    )


# --- Отправка ответа к вопросу --- #
@router.message(CreateAnswer.create_answer)
async def create_answer(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is not None and current_state != CreateAnswer.create_answer:
        await state.clear()

    data = await state.get_data()

    if not data:
        await state.clear()
        return await message.answer(text=no_state, reply_markup=profile_kb())

    cleaned_text = re.sub(r'[<>]', '', message.text)  # Убираем символы выделения
    if len(cleaned_text) < 4 or len(cleaned_text) > 1000:
        return await message.answer(text="❌ Текст должен быть не короче 4 и не длиннее 1.000 символов! Пожалуйста, повторите ввод:")

    question_id = data.get('question_id', None)
    get_user_response_json = data.get('user_response', None)

    async with httpx.AsyncClient() as client:
        create_answer_response = await client.post(message.bot.config['SETTINGS']['backend_url'] + 'create_answer', json={
            "login": get_user_response_json['login'],
            "question_id": question_id,
            "answer": cleaned_text
        })

    if create_answer_response.status_code == 200:
        await state.set_state(CreateAnswer.create_answer_photo)

        data['answer_id'] = create_answer_response.json()['id']
        data['answer'] = cleaned_text
        await state.update_data(data)

        # Возвращаемся к просмотру ленты
        await message.answer(
            text="🧡 Ответ готов! Вы можете прикрепить к нему фотографию или опубликовать без неё:",
            reply_markup=finish_answers_btns().as_markup()
        )
    else:
        await message.answer(text=server_error)


# --- Отправка ответа к вопросу --- #
@router.message(CreateAnswer.create_answer_photo)
async def create_answer_photo(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is not None and current_state != CreateAnswer.create_answer_photo:
        await state.clear()

    data = await state.get_data()

    # Проверка на существование формы для заполнения
    if not data:
        await state.clear()
        return await message.answer(text=no_state, reply_markup=profile_kb())

    if message.photo:
        answer_id = data.get('answer_id', None)
        get_user_response_json = data.get('user_response', None)

        letters = string.ascii_letters + string.digits

        file_path = f"bot/assets/answers/{answer_id}_{get_user_response_json['login']}_{''.join(random.choice(letters) for _ in range(7))}.png"
        await message.bot.download(
            message.photo[-1],
            destination=file_path
        )

        await message.answer(
            text="🧡 Ответ готов! Вы можете отправить новую фотографию (для замены) или опубликовать!",
            reply_markup=finish_answers_btns().as_markup()
        )
    else:
        await message.answer(text="❌ Прикрепите фотографию или завершите заполение!")


# --- Финал --- #
@router.callback_query(F.data == "finish_answers")
async def finish_answers(callback: CallbackQuery, state: FSMContext):# -
    data = await state.get_data()

    # Удаляем кнопку с сообщения
    await remove_button(msg=callback.message, state=state)

    # Проверка на сохранение данных. Берём самое последнее (contacts)
    if not data.get('user_response', None):
        await state.clear()
        return await callback.message.answer(text=no_state)

    answer_id = data.get('answer_id', None)
    question_id = data.get('question_id', None)
    get_user_response_json = data.get('user_response', None)
    answer = data.get('answer', None)

    await callback.message.answer(
        text="🧡✅ Ответ готов и передан на модерацию! Мы уведомим вас о решении, не выходите из аккаунта!",
        reply_markup=profile_kb()
    )
    
    # Отправляем сообщение автору
    async with httpx.AsyncClient() as client:
        get_question_response = await client.get(
            f"{callback.bot.config['SETTINGS']['backend_url']}get_question?question_id={question_id}"
        )

    if get_question_response.status_code == 200 and get_question_response.json():
        if get_question_response.json()['is_subscribe'] is True:
            get_user_response = await check_account_login(
                config=callback.bot.config,
                login=get_question_response.json()['login_id']
            )
            # * .json() -> [{'user_info'}: ..., {'user_subsribes'}: ..., {'user_statistic'}: ..., {'user_privileges'}: ..., {'blacklist_info'}: ...]

            photo_path = find_photo_in_folder(folder_path="bot/assets/answers", id=answer_id)
            if photo_path:
                await callback.bot.send_photo(
                    chat_id=get_user_response.json()['user_info']['user_id'],
                    photo=FSInputFile(path=photo_path),
                    caption=f"<b>😉 Новый ответ с картинкой!</b>\n\
                        \nНа ваш вопрос: <i>{get_question_response.json()['question']}</i> поступил ответ от <code>{get_user_response_json['login']}</code>:\
                        \n\nНе промодерирован\
                        \n{answer}"   
                )
            else:
                await callback.bot.send_message(
                    chat_id=get_user_response.json()['user_info']['user_id'],
                    text=f"<b>😉 Новый ответ!</b>\n\
                        \nНа ваш вопрос: <i>{get_question_response.json()['question']}</i> поступил ответ от <code>{get_user_response_json['login']}</code>:\
                        \n\nНе промодерирован\
                        \n{answer}"
                )


# === Редактирование ответов ===


# --- Изменение ответа -> финиш --- #
@router.message(EditQuestionOrAnswer.edit_answer)
async def edit_answer_choice(message: Message, state: FSMContext):
    data = await state.get_data()

    if not data:
        await state.clear()
        return await message.answer(text=no_state, reply_markup=profile_kb())

    cleaned_text = re.sub(r'[<>]', '', message.text.capitalize())  # Убираем символы выделения
    if len(cleaned_text) < 4 or len(cleaned_text) > 1000:
        return await message.answer(text="❌ Текст должен быть не короче 4 и не длиннее 1.000 символов! Пожалуйста, повторите ввод:")

    my_response = data.get('user_response', None)
    answer_id = data.get("answer_id", 1)

    async with httpx.AsyncClient() as client:
        update_answer_response = await client.put(message.bot.config['SETTINGS']['backend_url'] + 'update_answer', json={
            "answer_id": answer_id,
            "login": my_response['login'],
            "answer": cleaned_text,
        })

    if update_answer_response.status_code == 200:
        await state.set_state(Searching.tape_answers)

        await message.answer(
            text="🧡✅ Ответ отредактирован и передан на модерацию! Мы уведомим вас о решении, не выходите из аккаунта!",
            reply_markup=my_answers_kb()
        )

        await send_searching_answers(
            message=message,
            state=state,
            question_id=data.get("question_id", 1),
            my_response=my_response,
            global_tape=False
        )
    else:
        await message.answer(text=server_error)
