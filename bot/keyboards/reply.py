from aiogram import types


start_btns = [
        [types.KeyboardButton(text="Начать игру")],
    ]
start_kb = types.ReplyKeyboardMarkup(keyboard=start_btns, resize_keyboard=True)

is_correct_players_btns = [
        [types.KeyboardButton(text="Да")],
        [types.KeyboardButton(text="Нет")],
    ]
is_correct_players_kb = types.ReplyKeyboardMarkup(keyboard=is_correct_players_btns, resize_keyboard=True)