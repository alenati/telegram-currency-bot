import psycopg2
from config import host, user, password, db_name
from parser import lines

try:
    connection = psycopg2.connect(
        host = host,
        user = user,
        password = password,
        database = db_name
    )

    with connection.cursor() as cursor:

        insert_q = """ 
        insert into currency_cost (currency_num,unit,rate,date) values (%s,%s,%s,%s) 
        """

        for line in lines:
            cursor.execute(insert_q,line)

        connection.commit()

        cursor.execute(
            "select * from currency_cost;"
        )

        rows = cursor.fetchall()

        for row in rows:
            print(row)

except Exception as ex:
    print("mistake ", ex)
finally:
    if connection:
        connection.close()
        print("connection closed")