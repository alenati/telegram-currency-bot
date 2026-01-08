from aiogram.fsm.state import State, StatesGroup

class CurrState(StatesGroup):
    view = State()
    subs = State()
    unsubs = State()
    graph = State()
    today_news = State()
    date_news = State()
    month_news = State()
    random_news = State()

class LangState(StatesGroup):
    en = State()
    ru = State()

class FormatState(StatesGroup):
    txt = State()
    non_txt = State()