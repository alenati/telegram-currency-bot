from aiogram import Router
from aiogram.filters import Command
from aiogram import types
from aiogram.fsm.context import FSMContext
import functions 
import states
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import buttonlist
import pytz
from datetime import datetime, timedelta

router_commands = Router()

@router_commands.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Hello! Choose language using /language (ru, sk, en)")

@router_commands.message(Command("help"))
async def help(message:types.Message):
    await message.answer("Help!")

@router_commands.message(Command("subscribe"))
async def subscribe(message:types.Message, state: FSMContext):
    new_keyboard = await functions.get_custom_keyboard(message.from_user.id, "unsub")
    await message.answer("Выбери валюту из списка или напиши её код (в формате XXX или /XXX) для подписки:", reply_markup=new_keyboard)
    await state.set_state(states.CurrState.subs)

@router_commands.message(Command("unsubscribe"))
async def unsubscribe(message:types.Message, state: FSMContext):
    new_keyboard = await functions.get_custom_keyboard(message.from_user.id, "sub")
    await message.answer("Выбери валюту из списка или напиши её код (в формате XXX или /XXX) для отписки:", reply_markup=new_keyboard)
    await state.set_state(states.CurrState.unsubs)


@router_commands.message(Command("currency"))
async def subscribe(message: types.Message, state: FSMContext):
    await state.set_state(states.CurrState.view)
    keyboard = ReplyKeyboardMarkup(
        keyboard = buttonlist.buttons,
        resize_keyboard = True,
        one_time_keyboard = True
    )
    await message.answer("Выбери валюту из списка или напиши её код (в формате XXX или /XXX) для просмотра подробной информации по валюте:", reply_markup=keyboard)

@router_commands.message(Command("graph"))
async def generate_graph(message: types.Message, state: FSMContext):
    await state.set_state(states.CurrState.graph)
    keyboard = ReplyKeyboardMarkup(
        keyboard = buttonlist.buttons,
        resize_keyboard = True,
        one_time_keyboard = True
    )
    await message.answer("Выбери валюту из списка для генерации графика:", reply_markup=keyboard)

@router_commands.message(Command("news"))
async def news(message: types.Message):

    keyboard_news = ReplyKeyboardMarkup(
    keyboard = [
        [KeyboardButton(text="Сегодня")],
        [KeyboardButton(text="По дате")],
        [KeyboardButton(text="Все за месяц")],
        [KeyboardButton(text="Рандомная новость")]],
    resize_keyboard = True,
    one_time_keyboard = True
    )
    await message.answer("Выбери, за какой период отобразить новости:",reply_markup=keyboard_news)


@router_commands.message(Command("today"))
async def today (message: types.Message):
    moscow_tz = pytz.timezone('Europe/Moscow')
    moscow_time = datetime.now(moscow_tz)

    last_dates = await functions.get_last_date()
    last_date_li = last_dates[0]
    date_obj = last_date_li['date']
    last_date_str =date_obj.strftime("%Y-%m-%d")
    last_date = datetime.strptime(last_date_str, "%Y-%m-%d").date()
    print(last_date)
    records = await functions.get_last_updates(last_date)
    format_last_date = last_date.strftime("%d.%m.%Y")
    answer = ""
    answer += (f"На сегодня, {moscow_time.day}.{moscow_time.month}.{moscow_time.year} {moscow_time.hour}:{moscow_time.minute} по МСК, действует курс валют, "
                f"обновленный {format_last_date} в 12:00 по МСК.\n\n")
    for record in records:
        answer += f"{record['currency_name']} ({record['currency_code']}):\n{record['unit']} за {record['rate']} Российских рублей (RUR)\n\n"

    await message.answer(answer)
