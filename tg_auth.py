from aiogram import Bot, Dispatcher
import os 
from dotenv import load_dotenv
# import asyncio
import logging
# from logging_config import setup_logger



async def tg_handshake():
    load_dotenv()
    bot = Bot(token=os.getenv("TG_API_KEY"))
    # setup_logger()
    try:
        me = await bot.get_me()
        logging.info(f"[TELEGRAM AUTH] Successful")
        logging.info(f"[TELEGRAM AUTH] Bot: @{me.username}")
    except Exception as e:
        logging.error("[TELEGRAM AUTH] Fail")
        return
    finally:
        await bot.session.close()
    return


# if __name__ == "__main__":
#     asyncio.run(main())
