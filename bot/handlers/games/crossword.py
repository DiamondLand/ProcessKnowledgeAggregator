from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from functions.crosswords.tasks import crossword
from functions.crosswords.shows import show_crossword

from events.states_group import Utilits

router = Router()


@router.message(Utilits.crossword_input)
async def fill_crossword(message: Message, state: FSMContext):
    guessed_word = message.text.strip().lower()

    for coords, data in crossword.items():
        if guessed_word == data['answer']:
            if not data['guessed']:
                crossword[coords]['guessed'] = True
                await message.answer(f"💚 Правильно! {guessed_word.capitalize()} вычеркнуто из кроссворда!")
                return await show_crossword(message, state=state)
            else:
                await message.answer("💥 Это слово уже было угадано!")
                return await show_crossword(message, state=state)

    await message.answer("💔 Не верно! Попробуйте еще раз:")
    return await show_crossword(message, state=state)
