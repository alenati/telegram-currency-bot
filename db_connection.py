import asyncpg
import logging
from config import Config

#to run: await connect()

async def connect():
    connection = await asyncpg.connect(
                host = Config.PG_HOST,
                user = Config.PG_USER,
                password = Config.PG_PASSWORD,
                database = Config.PG_DB_NAME
            )
    if connection: 
        logging.info("[POSTGRES AUTH] Successful")
        return connection
    else:
        logging.error("[POSTGRES AUTH] Failed")
    
# if __name__ == '__main__':
#     asyncio.run(connect())