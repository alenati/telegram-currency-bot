import psycopg2
from config import host, user, password, db_name

try:
    connection = psycopg2.connect(
        host = host,
        user = user,
        password = password,
        database = db_name
    )

    with connection.cursor() as cursor:
        cursor.execute(
            "select * from currency;"
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