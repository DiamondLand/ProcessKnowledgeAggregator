import httpx

from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from elements.keyboards.keyboards_profile import profile_kb
from elements.keyboards.text_on_kb import cancel_button, back, leaders

from handlers.commands.commands_handler import cmd_start

from .states_group import Captcha

router = Router()


# --- Завершение заполнения формы --- #
@router.message(F.text == cancel_button)
async def cancel_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == Captcha.captcha_input:
        return await message.answer(text="❌ Данное действие нельзя прервать!")

    if current_state is None:
        return await message.answer(
            text="Нет действий, которые можно было бы прервать!",
            reply_markup=ReplyKeyboardRemove()
        )

    await state.clear()
    await message.answer(
        text="<b>Действие прервано!</b>\nДля возвращения в главную панель воспользуйтесь /profile!",
        reply_markup=ReplyKeyboardRemove()
    )


# --- Возвращение в панель аккаунтав --- #
@router.message(F.text == back)
async def back_handler(message: Message, state: FSMContext):
    # Если стадия существует, выходим из неё
    current_state = await state.get_state()
    if current_state is not None:
        await state.clear()

    await cmd_start(message=message, state=state)


# --- Обработчик ввода каптчи --- #
@router.message(Captcha.captcha_input)
async def check_captcha(message: Message, state: FSMContext):
    data = await state.get_data()
    captcha_text = data.get('captcha_text', '')
    if message.text == captcha_text:
        await state.clear()
        await message.answer(
            text="Проверка на робота пройдена! Продолжим 😉?",
            reply_markup=profile_kb()
        )
    else:
        await message.answer(
            text=f"❌ Не верно! Повторите ввод: <strike><b>{captcha_text}</b></strike>",
            reply_markup=ReplyKeyboardRemove()
        )


# --- Панель лидеров --- #
@router.message(F.text == leaders)
async def leaders_handler(message: Message, state: FSMContext):
    # Если стадия существует, выходим из неё
    current_state = await state.get_state()
    if current_state is not None:
        await state.clear()

    async with httpx.AsyncClient() as client:
        get_users_response = await client.get(
            f"{message.bot.config['SETTINGS']['backend_url']}get_users"
        )
    # * .json() -> [{'user_info'}: ..., {'user_subsribes'}: ..., {'user_statistic'}: ..., {'user_privileges'}: ..., {'blacklist_info'}: ...]

    if get_users_response.status_code == 200 and get_users_response.json():
        text = "ЛИДЕРЫ:\n\n"

        for user_data in get_users_response.json():
            user_info = user_data.get('user_info', {})
            user_statistics = user_data.get('user_statistic', None)

            if user_statistics:
                for user_statistic in user_statistics:
                    login_id = user_statistic.get('login_id', '')
                    answers = user_statistic.get('answers', 0)
                    questions = user_statistic.get('questions', 0)
                    points = user_statistic.get('points', 0)

                    contacts = user_info.get('contacts', '')

                    user_info_str = f"<b>Пользователь:</b> <code>{login_id}</code>."
                    if contacts:
                        user_info_str += f" <b>Контакты:</b> <code>{contacts}</code>\n"
                    user_info_str += f"Ответов: <code>{answers}</code> | Вопросов: <code>{questions}</code> | Поинтов: <code>{points}</code>\n\n"

                    text += user_info_str
            else:
                text += "Данные о статистике пользователя отсутствуют\n"

        await message.answer(text=text)
