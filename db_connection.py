import asyncpg
from dotenv import load_dotenv
import os 
import logging
# from logging_config import setup_logger

#to run: await connect()

async def connect():
    # setup_logger()
    # logger = logging.getLogger(__name__)
    load_dotenv()
    connection = await asyncpg.connect(
                host = os.getenv("PG_HOST"),
                user = os.getenv("PG_USER"),
                password = os.getenv("PG_PASSWORD"),
                database = os.getenv("PG_DB_NAME")
            )
    if connection: 
        logging.info("[POSTGRES AUTH] Successful")
        return connection
    else:
        logging.error("[POSTGRES AUTH] Failed")
    
# if __name__ == '__main__':
#     asyncio.run(connect())