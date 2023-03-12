from aiogram.dispatcher.filters.state import State, StatesGroup


class Acquaintance(StatesGroup):
    waiting_for_name = State()
    waiting_for_confirm = State()
    waiting_for_end_game = State()