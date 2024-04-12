from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from events.states_group import Utilits

router = Router()


# Карта кроссворда
crossword = {
    (0, 0): {'hint': 'Часть машины, отвечающая за преобразование энергии', 'answer': 'двигатель', 'guessed': False},
    (0, 4): {'hint': 'Механизм для передачи движения внутри машины', 'answer': 'трансмиссия', 'guessed': False},
    (2, 2): {'hint': 'Устройство для сборки и разборки деталей', 'answer': 'монтажник', 'guessed': False},
    (3, 0): {'hint': 'Тип топлива, используемый внутренними сгораемыми двигателями', 'answer': 'бензин', 'guessed': False},
    (4, 3): {'hint': 'Деталь машины, преобразующая круговое движение в прямолинейное', 'answer': 'шатун', 'guessed': False}
}

async def show_crossword(message: Message, state: FSMContext):
    crossword_str = ''
    for y in range(5):
        for x in range(5):
            cell = crossword.get((x, y))
            if cell:
                if cell['guessed']:
                    crossword_str += f"<strike>{cell['hint']}</strike> <code>[{cell['answer']}]</code>\n\n"
                else:
                    crossword_str += f"{cell['hint']} [ ]\n\n"
    await state.set_state(Utilits.crossword_input)
    await message.answer(crossword_str)


@router.message(Utilits.crossword_input)
async def fill_crossword(message: Message, state: FSMContext):
    guessed_word = message.text.strip().lower()

    for coords, data in crossword.items():
        if guessed_word == data['answer']:
            crossword[coords]['guessed'] = True
            await show_crossword(message, state=state)
            return await message.answer(f"Правильно! {guessed_word.capitalize()} вычеркнуто в кроссворде.")

    await message.answer("Неверно! Попробуйте еще раз.")
