import asyncio

from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from events.states_group import Captcha

from .captcha_text import generate_captcha_text

MIN_TIME_BETWEEN_MESSAGES = 3.5
MAX_MESSAGES_BETWEEN = 4


# --- Проверка частоты отправки сообщений --- #
async def is_suspected_robot(state: FSMContext) -> bool:
    loop = asyncio.get_event_loop()
    user_state = await state.get_state()

    # Если состояние не существует
    if not user_state:
        return False

    # Если это первая команда после истечения интервала, обновляем время и количество команд
    if user_state == 1:
        await state.update_data(last_command_time=loop.time(), command_count=1)
    else:
        data = await state.get_data()
        last_command_time = data.get('last_command_time', 0)
        command_count = data.get('command_count', 0)
        current_time = loop.time()

        # Если прошло ли достаточно времени с момента последней команды пользователя, обновляем таймер и команды
        if current_time - last_command_time > MIN_TIME_BETWEEN_MESSAGES:
            await state.update_data(last_command_time=current_time, command_count=1)
        else:
            # Если количество команд за интервал превышает допустимые
            if command_count >= MAX_MESSAGES_BETWEEN:
                return True
            else:
                await state.update_data(command_count=command_count+1)
    return False


# --- Действия при подозрении на робота --- #
async def handle_suspected_robot(message: Message, state: FSMContext):
    await state.set_state(Captcha.captcha_input)

    data = await state.get_data()
    captcha_text = generate_captcha_text()
    data['captcha_text'] = captcha_text
    await state.update_data(data)

    await message.answer(
        text=f"<b>⚠️ Проверка на робота❗</b>\n\nПеред продолжением просмотра анкет, пожалуйста, введите следующий текст: <strike><b>{captcha_text}</b></strike>",
        reply_markup=ReplyKeyboardRemove()
    )
