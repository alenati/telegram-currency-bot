import psycopg2
from config import host, user, password, db_name

def get_last_curr_info(currency_code):
    try:
        connection = psycopg2.connect(
            host = host,
            user = user,
            password = password,
            database = db_name
        )

        with connection.cursor() as cursor:
            query = """
            select date, round(rate/unit,4), currency_num from currency_cost
            where currency_num = %s
            order by date desc 
            limit 1
            """
            cursor.execute(query,(currency_code,))
            print(cursor.fetchall())

    except Exception as ex:
        print("mistake ", ex)
    finally:
        if connection:
            connection.close()
            print("connection closed")


get_last_curr_info('360')