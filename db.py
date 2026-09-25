import psycopg2
from config import host, user, password, db_name
from parser import lines
from datetime import datetime

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
            date_str = line[3] 
            parsed_date = datetime.strptime(date_str, "%d.%m.%Y").date()

            new_line = (line[0], line[1], line[2], parsed_date)

   
            cursor.execute(insert_q,new_line)

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