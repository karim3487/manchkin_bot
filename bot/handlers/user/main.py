from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import ReplyKeyboardRemove

from bot.keyboards.reply import start_kb, is_correct_players_kb
from bot.states.users.main import Acquaintance


async def start(msg: Message, state: FSMContext):
    await msg.answer("Привет! Это бот для ведения игры манчкин", reply_markup=start_kb)
    await state.finish()


async def start_game(msg: Message, state: FSMContext):
    await msg.reply("Введите имена игроков через пробел:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(Acquaintance.waiting_for_name.state)


async def add_players(msg: Message, state: FSMContext):
    players = msg.text.replace(',', '').split(' ')

    await state.update_data(players=[players])
    await msg.answer(f'Все правильно?\n<code>{", ".join(players)}</code>', reply_markup=is_correct_players_kb)
    await state.set_state(Acquaintance.waiting_for_confirm.state)


async def confirm_players(msg: Message, state: FSMContext):
    if msg.text.lower() == 'да':
        players = await state.get_data()
        players = players['players'][0]
        players_btns = []
        for i, player in enumerate(players):
            players_btns.append([])
            line = players_btns[i]
            line.append(KeyboardButton(text=f"{player} -1"))
            line.append(KeyboardButton(text=f"{player} +1"))
        players_btns.append([KeyboardButton(text="Закончить игру")])
        players_kb = ReplyKeyboardMarkup(keyboard=players_btns, resize_keyboard=True)

        await msg.answer("Отлично! Начинаем...")

        board = [f'{player}: 1\n' for player in players]
        board = ''.join(board)
        await msg.answer(f"{board}", reply_markup=players_kb)
        await state.update_data(board=board)
        await state.set_state(Acquaintance.waiting_for_end_game.state)
    elif msg.text.lower() == 'нет':
        await msg.reply("Тогда введите имена игроков через пробел еще раз:")
        await state.set_state(Acquaintance.waiting_for_name.state)


async def game(msg: Message, state: FSMContext):
    if msg.text == 'Закончить игру':
        await msg.answer('Игра окончена', reply_markup=start_kb)
        await state.finish()
        return

    data = await state.get_data()
    players = data['players'][0]
    players_plus = [f'{player} +1' for player in players]
    players_minus = [f'{player} -1' for player in players]
    players = players_plus + players_minus
    if msg.text not in players:
        await msg.answer("Пожалуйста, выберите игрока, используя клавиатуру ниже.")
        return

    board = data['board']
    players_score = board.split('\n')

    operation = msg.text.split(' ')[1][-2]
    name = msg.text.split(' ')[0]
    if operation == '+':
        for i in range(len(players_score)):
            if name in players_score[i]:
                player, score = tuple(players_score[i].split(': '))
                if int(score) < 9:
                    players_score[i] = f'{player}: {int(score) + 1}'
                else:
                    await msg.answer(f'{player} победил!\nИгра окончена!', reply_markup=start_kb)
                    await state.finish()
                    return
        board = '\n'.join(players_score)
    else:
        for i in range(len(players_score)):
            if name in players_score[i]:
                player, score = tuple(players_score[i].split(': '))
                if int(score) > 1:
                    players_score[i] = f'{player}: {int(score) - 1}'
                else:
                    await msg.answer(f'Нельзя так делать!')
                    return
        board = '\n'.join(players_score)

    await state.update_data(board=board)
    await msg.answer(board)







def register_user_handlers(dp: Dispatcher):
    dp.register_message_handler(start, commands=['start'], state='*')
    dp.register_message_handler(start_game, Text(equals="Начать игру"))
    dp.register_message_handler(add_players, content_types=['text'], state=Acquaintance.waiting_for_name.state)
    dp.register_message_handler(confirm_players, content_types=['text'], state=Acquaintance.waiting_for_confirm.state)
    dp.register_message_handler(game, content_types=['text'],
                                state=Acquaintance.waiting_for_end_game.state)
