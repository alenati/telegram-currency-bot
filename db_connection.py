import asyncpg
from config import host, user, password, db_name, api_key
import asyncio

#to run: await connect()

async def connect():
    connection = await asyncpg.connect(
                host = host,
                user = user,
                password = password,
                database = db_name
            )
    return connection
