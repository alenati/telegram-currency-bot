from aiogram.fsm.state import State, StatesGroup

class CurrState(StatesGroup):
    view = State()
    subs = State()
    unsubs = State()
    graph = State()