import asyncpg
from dotenv import load_dotenv
import os 

#to run: await connect()

async def connect():
    load_dotenv()
    connection = await asyncpg.connect(
                host = os.getenv("PG_HOST"),
                user = os.getenv("PG_USER"),
                password = os.getenv("PG_PASSWORD"),
                database = os.getenv("PG_DB_NAME")
            )
    return connection
