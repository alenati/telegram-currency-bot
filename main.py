import asyncpg
import asyncio
import pytz
from datetime import datetime
from aiogram import Bot,Dispatcher,types
from aiogram.filters import Command
from config import host, user, password, db_name, api_key
from messages import start_m, help_m

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
        select curr.currency_name, cost.unit, cost.rate, curr.currency_code 
    from currency_cost cost 
    join currency curr on curr.currency_num = cost.currency_num
    where date = $1
        """

        result = await connection.fetch(query,moscow_date)
        print(result)
    except Exception as ex:
        print("mistake: ", ex)
    finally:
        await connection.close()
        print("connection close")




async def main():
    #await get_last_curr_info('978')
    #await get_curr_name('978')
    #await get_num_subscribers('978')

    moscow_tz = pytz.timezone('Europe/Moscow')
    moscow_time = datetime.now(moscow_tz)
    moscow_date = moscow_time.date()
   
    if await get_last_updates(moscow_date):
        print("sucess")

    bot = Bot(token = api_key)
    dp = Dispatcher()

    @dp.message(Command("start"))
    async def start(message: types.Message):
        await message.answer(start_m)

    @dp.message(Command("help"))
    async def help(message:types.Message):
        await message.answer(help_m)

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())