# Two nodes:
#   1. Dotenv check
#   2. Loop

import tg_auth
import db_connection 
from handlers.commands import router_commands
from handlers.news import router_news
from handlers.donate import router_donate 
from handlers.generic import router_generic
import logging 
from logging_config import setup_logger
import asyncio
from aiogram import Bot,Dispatcher
import os
from dotenv import load_dotenv



async def main():
    load_dotenv()

    setup_logger()
    logging.info("[NODE 1] Starting")

    # First Node: .env check 
    #   First Stage: TG AUTH
    await tg_auth.tg_handshake()

    #   Second Stage: Postgres AUTH
    await db_connection.connect()

    #   Third Stage: Mongo Auth
    #   Skip for now 

    #   Fourth Stage: News API
    #   Skip for now

    logging.info("[NODE 2] Starting")

    # Second Node: loop 
    tg_api_key = os.getenv("TG_API_KEY")
    bot = Bot(token = tg_api_key)
    dp = Dispatcher()
    dp.include_router(router_commands)
    dp.include_router(router_news)
    dp.include_router(router_donate)
    dp.include_router(router_generic)
    await dp.start_polling(bot)
  

if __name__ == '__main__':
    asyncio.run(main())