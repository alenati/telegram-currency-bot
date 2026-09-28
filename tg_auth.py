from aiogram import Bot
import logging
from config import Config



async def tg_handshake():
    bot = Bot(token=Config.TG_API_KEY)
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
