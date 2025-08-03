import asyncpg
import psycopg2
import asyncio
from config import host, user, password, db_name

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


async def main():
    await get_last_curr_info('978')
    await get_curr_name('978')


if __name__ == '__main__':
    asyncio.run(main())