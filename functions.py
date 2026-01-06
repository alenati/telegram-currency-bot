from db_connection import connect
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
from datetime import datetime, timedelta
from buttonlist import buttons
import re
from aiogram.types import BufferedInputFile

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

async def get_curr_code(curr_num):
    try:
        connection = await connect()


        query = """
           select currency_code from currency
           where currency_num = $1
           """
        result = await connection.fetch(query,curr_num)
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

async def get_historical_info(currency_num):
    try:
        connection = await connect()
        query = """
        select date, rate, unit from currency_cost where currency_num = $1
        """
        result = await connection.fetch(query, currency_num)

        return result

    except Exception as e:
        print("mistake", e)
    finally:
        pass

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

#param can be "str" - if you want it in string format 
#and "date" - if you want to work with date
async def get_time(time_record, param):
    date_str = time_record.strftime("%Y-%m-%d")
    date = datetime.strptime(date_str, "%Y-%m-%d").date()
    if param == "str":
        return date_str
    elif param == "date":
        return date

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

#param can be "sub" - to get sub keyboard
#"unsub" - to get unsub keyboard
async def get_custom_keyboard(user_id, param):
    subs = await get_subscription_list(user_id)
    subscribed = []
    for i in range(len(subs)):
        subscribed.append(subs[i]["currency_code"])
    unsubcribed_buttons = []
    for row in buttons:
        new_row = []
        for button in row:
            match_in_button = re.search(r'\b[A-Z]{3}\b', button.text)
            if not match_in_button:
                continue
            curr_code = match_in_button.group()

            if param == "sub":
                if curr_code in subscribed:
                    new_row.append(button)
            elif param == "unsub":
                if curr_code not in subscribed:
                    new_row.append(button)
        if new_row:
            unsubcribed_buttons.append(new_row)
    
    new_keyboard = ReplyKeyboardMarkup(
        keyboard = unsubcribed_buttons,
        resize_keyboard=True,
        one_time_keyboard=True
    )

    return new_keyboard

async def get_graph(dates, rates, unit, curr_code):
        
        matplotlib.use("Agg")
        plt.figure(figsize=(8, 4))
        plt.plot(dates, rates, marker="o")
        plt.grid(True)
        plt.title(f'Курс {curr_code} к RUR. Цена за {unit} {curr_code}')
        plt.xlabel("Дата")
        plt.xticks(rotation=90)
        plt.ylabel("Курс (RUR)")


        buf = BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight")
        plt.close()
        buf.seek(0)

        image = BufferedInputFile(
        buf.getvalue(),
        filename="graph.png"
        )
        return image

# async def get_last_curr_info(currency_num):
#     try:
#         connection = await connect()

#         query = """
#         select date, rate, unit, currency_num from currency_cost
#         where currency_num = $1
#         order by date desc 
#         limit 1
#         """

#         result = await connection.fetch(query,currency_num)
#         return result

#     except Exception as ex:
#         print("mistake ", ex)
#     finally:
#         if connection:
#             await connection.close()
#             print("connection closed")
