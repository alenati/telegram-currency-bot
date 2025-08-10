import asyncpg
import asyncio
import pytz
from datetime import datetime, timedelta
from aiogram import Bot,Dispatcher,types
from aiogram.filters import Command
from config import host, user, password, db_name, api_key
from buttonlist import buttons
from messages import start_m, help_m
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram import F
import re

async def get_last_curr_info(currency_num):
    try:
        connection = await asyncpg.connect(
            host = host,
            user = user,
            password = password,
            database = db_name
        )

        query = """
        select date, round(rate/unit,4) as cost, currency_num from currency_cost
        where currency_num = $1
        order by date desc 
        limit 1
        """

        result = await connection.fetch(query,currency_num)
        print(result)

    except Exception as ex:
        print("mistake ", ex)
    finally:
        if connection:
            await connection.close()
            print("connection closed")

async def get_curr_num(currency_code):
    try:
        connection = await asyncpg.connect(
            host = host,
            user = user,
            password = password,
            database = db_name
        )
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
        connection = await asyncpg.connect(
            host=host,
            user=user,
            password=password,
            database=db_name
        )


        query = """
           select currency_name, currency_code from currency
           where currency_num = $1
           """
        result = await connection.fetch(query,currency_num)
        print(result)

    except Exception as ex:
        print("mistake ", ex)
    finally:
        if connection:
            await connection.close()
            print("connection closed")

async def get_num_subscribers(currency_num):
    try:
        connection = await asyncpg.connect(
            host = host,
            user = user,
            password = password,
            database = db_name
        )
        query = '''
            select coalesce((select count(user_id) from user_choice where currency_num = $1),0)
            as num_subscribers;
        '''

        result = await connection.fetch(query,currency_num)
        print(result)

    except Exception as ex:
        print("mistake", ex)
    finally:
        if connection:
            await connection.close()
            print("connection close")

async def get_last_updates(moscow_date):
    try:
        connection = await asyncpg.connect(
            host=host,
            user=user,
            password=password,
            database=db_name
        )

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
        connection = await asyncpg.connect(
            host = host,
            user = user,
            password = password,
            database = db_name
        )

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

        await message.answer(f"Информация о валюте:\n\n{message.text}\n\nЦифровой код валюты: {curr_num}\n")



    @dp.message(Command("subscribe"))
    async def subscribe(message: types.Message):
        await message.answer("Выбери валюту:", reply_markup=keyboard)



    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())