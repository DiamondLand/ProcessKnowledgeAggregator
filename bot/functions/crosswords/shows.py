from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from functions.crosswords.tasks import crossword

from events.states_group import Utilits


def is_crossword_solved():
    for cell in crossword.values():
        if not cell['guessed']:
            return False
    return True


async def show_crossword(message: Message, state: FSMContext):
    if is_crossword_solved():
        return await message.answer("🎉 Поздравляю! Вы успешно решили кроссворд!")

    crossword_str = ''
    for y in range(5):
        for x in range(5):
            cell = crossword.get((x, y))
            if cell:
                if cell['guessed']:
                    crossword_str += f"<strike>{cell['hint']}</strike> <code>[{cell['answer']}]</code>\n\n"
                else:
                    crossword_str += f"{cell['hint']} [{chr(10003) if cell['guessed'] else ' '}] \n\n"

    await state.set_state(Utilits.crossword_input)
    await message.answer(crossword_str)
