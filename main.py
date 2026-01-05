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

async def get_last_curr_info(currency_num):
    try:
        connection = await connect()

        query = """
        select date, rate, unit, currency_num from currency_cost
        where currency_num = $1
        order by date desc 
        limit 1
        """

        result = await connection.fetch(query,currency_num)
        return result

    except Exception as ex:
        print("mistake ", ex)
    finally:
        if connection:
            await connection.close()
            print("connection closed")

async def get_curr_num(currency_code):
    try:
        connection = await connect()
        query = """
        select currency_num from currency where currency_code = $1"""
        result = await connection.fetch(query,currency_code)
        return result

    except Exception as ex:
        print("mistake: ", ex)
    finally:
        if connection:
            await connection.close()
            print("connection closed")

async def get_curr_name(currency_num):
    try:
        connection = await connect()


        query = """
           select currency_name from currency
           where currency_num = $1
           """
        result = await connection.fetch(query,currency_num)
        return result

    except Exception as ex:
        print("mistake ", ex)
    finally:
        if connection:
            await connection.close()
            print("connection closed")

async def get_num_subscribers(currency_num):
    try:
        connection = await connect()
        query = '''
            select coalesce((select count(user_id) from user_choice where currency_num = $1),0)
            as num_subscribers;
        '''

        result = await connection.fetch(query,currency_num)
        return result

    except Exception as ex:
        print("mistake", ex)
    finally:
        if connection:
            await connection.close()
            print("connection close")

async def get_last_updates(moscow_date):
    try:
        connection = await connect()

        query = """
        select curr.currency_name as currency_name, cost.unit as unit, cost.rate as rate, curr.currency_code as currency_code 
    from currency_cost cost 
    join currency curr on curr.currency_num = cost.currency_num
    where date = $1
        """

        result = await connection.fetch(query,moscow_date)
        return result
    except Exception as ex:
        print("mistake: ", ex)
    finally:
        await connection.close()
        print("connection close")

async def get_last_date():
    try:
        connection = await connect()

        query = """
        select date from currency_cost order by date desc limit 1;
        """

        result = await connection.fetch(query)
        return result

    except Exception as ex:
        print("mistake: ", ex)
    finally:
        if connection:
            await connection.close()
            print("connection closed")

async def check_subscription(user_id, currency_num):
    try:
        connection = await connect()

        query = """
        select * from user_choice where user_id = $1 and currency_num = $2"""

        result = await connection.fetch(query, user_id, currency_num)

        return result
    except Exception as ex:
        print("mistake", ex)
    finally:
        if connection:
            await connection.close()
            print("connection closed")

async def new_subscription(user_id,currency_num):
    try:
        connection = await connect()
        query = """
        insert into user_choice (user_id, currency_num, created_at)
        values ($1, $2, current_date)
        """
        result = await connection.fetch(query, user_id, currency_num)
        return result
    except Exception as ex:
        print("mistake", ex)
    finally:
        if connection:
            await connection.close()
            print("connection closed")


async def unsubcribe(user_id, currency_num):
    try:
        connection = await connect()
        query = """
        delete from user_choice where user_id = $1 and currency_num = $2
        """
        result = await connection.fetch(query, user_id, currency_num)
        
        return result
    except Exception as ex:
        print("maistake", ex)
    finally:
        if connection:
            await connection.close()
            print("connection closed")       

async def get_subscription_list(user_id):
    try:
        connection = await connect()
        date = (await get_last_date())[0]['date']
        query = """
        select cy.currency_name, cy.currency_code, cc.unit, cc.rate from user_choice uc
        join currency_cost cc on uc.currency_num = cc.currency_num 
        join currency cy on cy.currency_num = uc.currency_num
        where date = $1 and user_id = $2;"""

        result = await connection.fetch(query,date, user_id)
        return result
    except Exception as ex:
        print("mistake ", ex)
    finally:
        if connection:
            await connection.close()
            print("connection closed")

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

    @dp.message(F.text.regexp(r'^[^\w]*([A-Z]{3})'))
    async def handle_curr_button(message: types.Message):
        curr_code = re.search(r'[A-Z]{3}', message.text).group()
        curr_num = (await get_curr_num(curr_code))[0]['currency_num']
        subs_num = (await  get_num_subscribers(curr_num))[0]['num_subscribers']
        last_info = await get_last_curr_info(curr_num)
        print(message.from_user.id)

        await message.answer(f"{message.text}\n\n"
                             f"Актуальный курс ЦБ РФ:\n\n{last_info[0]['unit']} {curr_code} за {last_info[0]['rate']} RUR\n\n"
                             f"/subscribe{curr_code} чтобы подписаться на валюту и ежедневно получать рассылку!\n\n"
                             f"Цифровой код валюты: {curr_num}\n\nКоличество подписчиков на валюту: {subs_num}\n\n")


    @dp.message(Command("currency"))
    async def subscribe(message: types.Message):
        await message.answer("Выбери валюту:", reply_markup=keyboard)

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


    @dp.message()
    async def subscribe_curr(message:types.Message):
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