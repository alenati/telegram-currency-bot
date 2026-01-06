import asyncpg
import asyncio
import pytz
from datetime import datetime, timedelta
from aiogram import Bot,Dispatcher,types
from aiogram.filters import Command
from config import api_key
from buttonlist import buttons
from messages import start_m, help_m
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram import F
import re
from db_connection import connect
import requests
from config import news_api_key
from aiogram.types import LabeledPrice
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
from aiogram.types import BufferedInputFile

from functions import get_last_curr_info, get_curr_num, get_curr_name, get_curr_code
from functions import get_num_subscribers, get_historical_info, get_last_updates, get_last_date
from functions import check_subscription, new_subscription, get_time, unsubcribe
from functions import get_subscription_list, get_custom_keyboard, get_graph


class CurrState(StatesGroup):
    view = State()
    subs = State()
    unsubs = State()
    graph = State()

async def main():
    #await get_last_curr_info('978')
    #await get_curr_name('978')
    #await get_num_subscribers('978')

    bot = Bot(token = api_key)
    dp = Dispatcher()

    @dp.message(Command("start"))
    async def start(message: types.Message):
        await message.answer(start_m)

    @dp.message(Command("help"))
    async def help(message:types.Message):
        await message.answer(help_m)

    @dp.message(Command("today"))
    async def today (message: types.Message):
        moscow_tz = pytz.timezone('Europe/Moscow')
        moscow_time = datetime.now(moscow_tz)

        last_dates = await get_last_date()
        last_date_li = last_dates[0]
        date_obj = last_date_li['date']
        last_date_str =date_obj.strftime("%Y-%m-%d")
        last_date = datetime.strptime(last_date_str, "%Y-%m-%d").date()
        print(last_date)
        records = await get_last_updates(last_date)
        format_last_date = last_date.strftime("%d.%m.%Y")
        answer = ""
        answer += (f"На сегодня, {moscow_time.day}.{moscow_time.month}.{moscow_time.year} {moscow_time.hour}:{moscow_time.minute} по МСК, действует курс валют, "
                   f"обновленный {format_last_date} в 12:00 по МСК.\n\n")
        for record in records:
            answer += f"{record['currency_name']} ({record['currency_code']}):\n{record['unit']} за {record['rate']} Российских рублей (RUR)\n\n"

        await message.answer(answer)

    keyboard = ReplyKeyboardMarkup(
        keyboard = buttons,
        resize_keyboard = True,
        one_time_keyboard = True
    )

    # @dp.message(F.text.regexp(r'^[^\w]*([A-Z]{3})'))
    # async def handle_curr_button(message: types.Message):
    #     curr_code = re.search(r'[A-Z]{3}', message.text).group()
    #     curr_num = (await get_curr_num(curr_code))[0]['currency_num']
    #     subs_num = (await  get_num_subscribers(curr_num))[0]['num_subscribers']
    #     last_info = await get_last_curr_info(curr_num)
    #     print(message.from_user.id)

    #     await message.answer(f"{message.text}\n\n"
    #                          f"Актуальный курс ЦБ РФ:\n\n{last_info[0]['unit']} {curr_code} за {last_info[0]['rate']} RUR\n\n"
    #                          f"/subscribe{curr_code} чтобы подписаться на валюту и ежедневно получать рассылку!\n\n"
    #                          f"Цифровой код валюты: {curr_num}\n\nКоличество подписчиков на валюту: {subs_num}\n\n")
        

    @dp.message(Command("clist"))
    async def clist(message: types.Message):
        rows = await get_subscription_list(message.from_user.id)
        ans = f"Ваши подписки:\n\n"
        for row in rows:
            ans += f"{row['currency_name']}: {row['unit']} {row['currency_code']} за {row['rate']} RUR\n\n"
        await message.answer(f"{ans}")


    @dp.message(Command("news"))
    async def news(message: types.Message):
        url = "https://newsapi.org/v2/top-headlines"
        parameters = {"category": "business", "apiKey": news_api_key}

        resp = requests.get(url, parameters)
        data = resp.json()
        ans = "Самые актуальные бизнес новости на сегодня:\n\n"
        for i in range(3):
            ans+= f'{data["articles"][i]["title"]}\n{data["articles"][i]["url"]}'
            if i != 2:
                ans += '\n\n'
        await message.answer(f"{ans}")

    @dp.message(Command("donate"))
    async def donate (message: types.Message):

        keyboard_donate = ReplyKeyboardMarkup(
        keyboard = [
            [KeyboardButton(text="10")],
            [KeyboardButton(text="50")],
            [KeyboardButton(text="100")]],
        resize_keyboard = True,
        one_time_keyboard = True
        )
        await message.answer("Выбери количество здезд, которые ты хочешь отправить:",reply_markup=keyboard_donate)

        
    @dp.pre_checkout_query()
    async def pre_checkout(pre_checkout_query: types.PreCheckoutQuery):
        await pre_checkout_query.answer(ok=True)

    @dp.message(F.successful_payment)
    async def success(message: types.Message):
        payload = message.successful_payment.invoice_payload

        if payload == "donation":
            await message.answer("Спасибо!")

    @dp.message(F.text.in_(["10", "50", "100"]))
    async def donate_amount(message: types.Message):
        amount = int(message.text)
        await message.answer_invoice(
                    title="Благодарность автору",
                    description = "Донат добровольный, не открывает доступ ни к каким функциям, не дает приемуществ, не влияет на работу бота.",
                    payload = f"donation{amount}{message.from_user.id}",
                    provider_token ="",
                    currency="XTR",
                    prices= [LabeledPrice(label="ДОНАТ", amount=amount)
                ],
                start_parameter=f"donate{amount}")
        
    @dp.message(Command("subscribe"))
    async def subscribe(message:types.Message, state: FSMContext):
        new_keyboard = await get_custom_keyboard(message.from_user.id, "unsub")
        await message.answer("Выбери валюту из списка или напиши её код (в формате XXX или /XXX) для подписки:", reply_markup=new_keyboard)
        await state.set_state(CurrState.subs)
    
    @dp.message(Command("unsubscribe"))
    async def unsubscribe(message:types.Message, state: FSMContext):
        new_keyboard = await get_custom_keyboard(message.from_user.id, "sub")
        await message.answer("Выбери валюту из списка или напиши её код (в формате XXX или /XXX) для отписки:", reply_markup=new_keyboard)
        await state.set_state(CurrState.unsubs)

    @dp.message(Command("currency"))
    async def subscribe(message: types.Message, state: FSMContext):
        await state.set_state(CurrState.view)
        await message.answer("Выбери валюту из списка или напиши её код (в формате XXX или /XXX) для просмотра подробной информации по валюте:", reply_markup=keyboard)

    @dp.message(Command("graph"))
    async def generate_graph(message: types.Message, state: FSMContext):
        await state.set_state(CurrState.graph)
        await message.answer("Выбери валюту из списка для генерации графика:", reply_markup=keyboard)
        
    @dp.message()
    async def handle_messages(message:types.Message, state: FSMContext):
        current_state = await state.get_state()

        if current_state == CurrState.view.state:
            curr_code = re.search(r'[A-Z]{3}', message.text).group()
            curr_num = (await get_curr_num(curr_code))[0]['currency_num']
            subs_num = (await  get_num_subscribers(curr_num))[0]['num_subscribers']
            last_info = await get_last_curr_info(curr_num)
            print(message.from_user.id)

            await message.answer(f"{message.text}\n\n"
                                f"Актуальный курс ЦБ РФ:\n\n{last_info[0]['unit']} {curr_code} за {last_info[0]['rate']} RUR\n\n"
                                f"/subscribe{curr_code} чтобы подписаться на валюту и ежедневно получать рассылку!\n\n"
                                f"Цифровой код валюты: {curr_num}\n\nКоличество подписчиков на валюту: {subs_num}\n\n")
            
        elif current_state == CurrState.subs.state:
            curr_code = re.search(r'[A-Z]{3}', message.text).group().upper()
            curr_num = (await get_curr_num(curr_code))[0]['currency_num']
            res = await check_subscription(message.from_user.id,curr_num)
            res1 = await check_subscription(message.from_user.id,'410')
            print(res)
            #print(res1)
            if res: #if subscription exist
                curr_name = (await get_curr_name(curr_num))[0]['currency_name']
                await message.answer(f"Вы уже подписаны на валюту {curr_code}, {curr_name}!\n\n"
                                     f"Больше информации о валюте:\n"
                                     f"/{curr_code}  ИЛИ  {curr_code.upper()}")
            else:
                curr_name = (await get_curr_name(curr_num))[0]['currency_name']
                await new_subscription(message.from_user.id, curr_num)
                await message.answer(f"Вы успешно подписались на валюту {curr_code}, {curr_name}!")
        elif current_state == CurrState.unsubs.state:
            curr_code = re.search(r'[A-Z]{3}', message.text).group().upper()
            curr_num = (await get_curr_num(curr_code))[0]['currency_num']
            res = await check_subscription(message.from_user.id,curr_num)
            if res:
                await unsubcribe(message.from_user.id, curr_num)
                await message.answer(f"Вы успешно отписались от валюты ({curr_code})!")
            else:
                await message.answer(f"Вы не были подписаны на эту валюту ({curr_code})!")
        elif current_state == CurrState.graph.state:
            await message.answer("Подождите генерацию графика...")
            curr_code = re.search(r'[A-Z]{3}', message.text).group().upper()
            curr_num = (await get_curr_num(curr_code))[0]['currency_num']
            res = await get_historical_info(curr_num)
            dates = []
            rates = []

            for row in res:
                dates.append(await get_time(row["date"], "str"))
                rates.append(float(row["rate"]))

            image = await get_graph(dates,rates,res[0]["unit"],curr_code)

            await message.answer_photo(
                photo=image,
                caption=f"График курса {curr_code}"
            )

        await state.clear()

        match = re.fullmatch(r'/subscribe([A-Za-z]{3})',message.text)

        if match:
            curr_code = match.group(1).upper()
            curr_num = (await get_curr_num(curr_code))[0]['currency_num']
            res = await check_subscription(message.from_user.id,curr_num)
            res1 = await check_subscription(message.from_user.id,'410')
            print(res)
            #print(res1)
            if res: #if subscription exist
                curr_name = (await get_curr_name(curr_num))[0]['currency_name']
                await message.answer(f"Вы уже подписаны на валюту {curr_code}, {curr_name}!\n\n"
                                     f"Больше информации о валюте:\n"
                                     f"/{curr_code}  ИЛИ  {curr_code.upper()}")
            else:
                curr_name = (await get_curr_name(curr_num))[0]['currency_name']
                await new_subscription(message.from_user.id, curr_num)
                await message.answer(f"Вы успешно подписались на валюту {curr_code}, {curr_name}!")

            #await message.answer(f"{message.from_user.id}, {curr_code}")

        
        match = re.fullmatch(r'/unsubscribe([A-Za-z]{3})',message.text)
        if match:
            curr_code = match.group(1).upper()
            curr_num = (await get_curr_num(curr_code))[0]['currency_num']
            res = await check_subscription(message.from_user.id,curr_num)
            if res:
                await unsubcribe(message.from_user.id, curr_num)
                await message.answer(f"Вы успешно отписались от валюты ({curr_code})!")
            else:
                await message.answer(f"Вы не были подписаны на эту валюту ({curr_code})!")
    





    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())