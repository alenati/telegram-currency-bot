# Two nodes:
#   1. Dotenv check
#   2. Loop

import tg_auth
import db_connection 
from handlers.commands import router_commands
from handlers.news import router_news
from handlers.donate import router_donate 

import logging 
from logging_config import setup_logger

import asyncpg
import asyncio
import pytz
from datetime import datetime, timedelta
from aiogram import Bot,Dispatcher,types
from aiogram.filters import Command
from config import api_key
from buttonlist import buttons
from messages import start_m, help_m
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram import F
import re
from db_connection import connect
import requests
from config import news_api_key
from aiogram.types import LabeledPrice
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
from aiogram.types import BufferedInputFile

from functions import get_last_curr_info, get_curr_num, get_curr_name, get_curr_code
from functions import get_num_subscribers, get_historical_info, get_last_updates, get_last_date
from functions import check_subscription, new_subscription, get_time, unsubcribe
from functions import get_subscription_list, get_custom_keyboard, get_graph, get_language_and_period

from states import CurrState, LangState, FormatState
from news_db import get_today_news


async def main():
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
    # TODO: bot infinite loop
    bot = Bot(token = api_key)
    dp = Dispatcher()
    dp.include_router(router_commands)
    await dp.start_polling(bot)

    

# async def main():
#     #await get_last_curr_info('978')
#     #await get_curr_name('978')
#     #await get_num_subscribers('978')

#     bot = Bot(token = api_key)
#     dp = Dispatcher()


#     keyboard = ReplyKeyboardMarkup(
#         keyboard = buttons,
#         resize_keyboard = True,
#         one_time_keyboard = True
#     )

#     # @dp.message(F.text.regexp(r'^[^\w]*([A-Z]{3})'))
#     # async def handle_curr_button(message: types.Message):
#     #     curr_code = re.search(r'[A-Z]{3}', message.text).group()
#     #     curr_num = (await get_curr_num(curr_code))[0]['currency_num']
#     #     subs_num = (await  get_num_subscribers(curr_num))[0]['num_subscribers']
#     #     last_info = await get_last_curr_info(curr_num)
#     #     print(message.from_user.id)

#     #     await message.answer(f"{message.text}\n\n"
#     #                          f"Актуальный курс ЦБ РФ:\n\n{last_info[0]['unit']} {curr_code} за {last_info[0]['rate']} RUR\n\n"
#     #                          f"/subscribe{curr_code} чтобы подписаться на валюту и ежедневно получать рассылку!\n\n"
#     #                          f"Цифровой код валюты: {curr_num}\n\nКоличество подписчиков на валюту: {subs_num}\n\n")
        

#     @dp.message(Command("clist"))
#     async def clist(message: types.Message):
#         rows = await get_subscription_list(message.from_user.id)
#         ans = f"Ваши подписки:\n\n"
#         for row in rows:
#             ans += f"{row['currency_name']}: {row['unit']} {row['currency_code']} за {row['rate']} RUR\n\n"
#         await message.answer(f"{ans}")








        
#     @dp.message()
#     async def handle_messages(message:types.Message, state: FSMContext):
#         current_state = await state.get_state()

#         if current_state == CurrState.view.state:
#             curr_code = re.search(r'[A-Z]{3}', message.text).group()
#             curr_num = (await get_curr_num(curr_code))[0]['currency_num']
#             subs_num = (await  get_num_subscribers(curr_num))[0]['num_subscribers']
#             last_info = await get_last_curr_info(curr_num)
#             print(message.from_user.id)

#             await message.answer(f"{message.text}\n\n"
#                                 f"Актуальный курс ЦБ РФ:\n\n{last_info[0]['unit']} {curr_code} за {last_info[0]['rate']} RUR\n\n"
#                                 f"/subscribe{curr_code} чтобы подписаться на валюту и ежедневно получать рассылку!\n\n"
#                                 f"Цифровой код валюты: {curr_num}\n\nКоличество подписчиков на валюту: {subs_num}\n\n")
            
#         elif current_state == CurrState.subs.state:
#             curr_code = re.search(r'[A-Z]{3}', message.text).group().upper()
#             curr_num = (await get_curr_num(curr_code))[0]['currency_num']
#             res = await check_subscription(message.from_user.id,curr_num)
#             res1 = await check_subscription(message.from_user.id,'410')
#             print(res)
#             #print(res1)
#             if res: #if subscription exist
#                 curr_name = (await get_curr_name(curr_num))[0]['currency_name']
#                 await message.answer(f"Вы уже подписаны на валюту {curr_code}, {curr_name}!\n\n"
#                                      f"Больше информации о валюте:\n"
#                                      f"/{curr_code}  ИЛИ  {curr_code.upper()}")
#             else:
#                 curr_name = (await get_curr_name(curr_num))[0]['currency_name']
#                 await new_subscription(message.from_user.id, curr_num)
#                 await message.answer(f"Вы успешно подписались на валюту {curr_code}, {curr_name}!")
#         elif current_state == CurrState.unsubs.state:
#             curr_code = re.search(r'[A-Z]{3}', message.text).group().upper()
#             curr_num = (await get_curr_num(curr_code))[0]['currency_num']
#             res = await check_subscription(message.from_user.id,curr_num)
#             if res:
#                 await unsubcribe(message.from_user.id, curr_num)
#                 await message.answer(f"Вы успешно отписались от валюты ({curr_code})!")
#             else:
#                 await message.answer(f"Вы не были подписаны на эту валюту ({curr_code})!")
#         elif current_state == CurrState.graph.state:
#             await message.answer("Подождите генерацию графика...")
#             curr_code = re.search(r'[A-Z]{3}', message.text).group().upper()
#             curr_num = (await get_curr_num(curr_code))[0]['currency_num']
#             res = await get_historical_info(curr_num)
#             dates = []
#             rates = []

#             for row in res:
#                 dates.append(await get_time(row["date"], "str"))
#                 rates.append(float(row["rate"]))

#             image = await get_graph(dates,rates,res[0]["unit"],curr_code)

#             await message.answer_photo(
#                 photo=image,
#                 caption=f"График курса {curr_code}"
#             )

#         if current_state in (CurrState.view, CurrState.subs, CurrState.unsubs, CurrState.graph):
#             await state.clear()


#         match = re.fullmatch(r'/subscribe([A-Za-z]{3})',message.text)

#         if match:
#             curr_code = match.group(1).upper()
#             curr_num = (await get_curr_num(curr_code))[0]['currency_num']
#             res = await check_subscription(message.from_user.id,curr_num)
#             res1 = await check_subscription(message.from_user.id,'410')
#             print(res)
#             #print(res1)
#             if res: #if subscription exist
#                 curr_name = (await get_curr_name(curr_num))[0]['currency_name']
#                 await message.answer(f"Вы уже подписаны на валюту {curr_code}, {curr_name}!\n\n"
#                                      f"Больше информации о валюте:\n"
#                                      f"/{curr_code}  ИЛИ  {curr_code.upper()}")
#             else:
#                 curr_name = (await get_curr_name(curr_num))[0]['currency_name']
#                 await new_subscription(message.from_user.id, curr_num)
#                 await message.answer(f"Вы успешно подписались на валюту {curr_code}, {curr_name}!")

#             #await message.answer(f"{message.from_user.id}, {curr_code}")

        
#         match = re.fullmatch(r'/unsubscribe([A-Za-z]{3})',message.text)
#         if match:
#             curr_code = match.group(1).upper()
#             curr_num = (await get_curr_num(curr_code))[0]['currency_num']
#             res = await check_subscription(message.from_user.id,curr_num)
#             if res:
#                 await unsubcribe(message.from_user.id, curr_num)
#                 await message.answer(f"Вы успешно отписались от валюты ({curr_code})!")
#             else:
#                 await message.answer(f"Вы не были подписаны на эту валюту ({curr_code})!")
    





#     await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())