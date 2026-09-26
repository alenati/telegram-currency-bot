from aiogram import Router
from aiogram import types
from aiogram.fsm.context import FSMContext
import functions 
import states
import re

router_generic = Router()

@router_generic.message()
async def handle_messages(message:types.Message, state: FSMContext):
    current_state = await state.get_state()

    if current_state == states.CurrState.view.state:
        curr_code = re.search(r'[A-Z]{3}', message.text).group()
        curr_num = (await functions.get_curr_num(curr_code))[0]['currency_num']
        subs_num = (await  functions.get_num_subscribers(curr_num))[0]['num_subscribers']
        last_info = await functions.get_last_curr_info(curr_num)
        print(message.from_user.id)

        await message.answer(f"{message.text}\n\n"
                            f"Актуальный курс ЦБ РФ:\n\n{last_info[0]['unit']} {curr_code} за {last_info[0]['rate']} RUR\n\n"
                            f"/subscribe{curr_code} чтобы подписаться на валюту и ежедневно получать рассылку!\n\n"
                            f"Цифровой код валюты: {curr_num}\n\nКоличество подписчиков на валюту: {subs_num}\n\n")
        
    elif current_state == states.CurrState.subs.state:
        curr_code = re.search(r'[A-Z]{3}', message.text).group().upper()
        curr_num = (await functions.get_curr_num(curr_code))[0]['currency_num']
        res = await functions.check_subscription(message.from_user.id,curr_num)
        res1 = await functions.check_subscription(message.from_user.id,'410')
        print(res)
        #print(res1)
        if res: #if subscription exist
            curr_name = (await functions.get_curr_name(curr_num))[0]['currency_name']
            await message.answer(f"Вы уже подписаны на валюту {curr_code}, {curr_name}!\n\n"
                                    f"Больше информации о валюте:\n"
                                    f"/{curr_code}  ИЛИ  {curr_code.upper()}")
        else:
            curr_name = (await functions.get_curr_name(curr_num))[0]['currency_name']
            await functions.new_subscription(message.from_user.id, curr_num)
            await message.answer(f"Вы успешно подписались на валюту {curr_code}, {curr_name}!")
    elif current_state == states.CurrState.unsubs.state:
        curr_code = re.search(r'[A-Z]{3}', message.text).group().upper()
        curr_num = (await functions.get_curr_num(curr_code))[0]['currency_num']
        res = await functions.check_subscription(message.from_user.id,curr_num)
        if res:
            await functions.unsubcribe(message.from_user.id, curr_num)
            await message.answer(f"Вы успешно отписались от валюты ({curr_code})!")
        else:
            await message.answer(f"Вы не были подписаны на эту валюту ({curr_code})!")
    elif current_state == states.CurrState.graph.state:
        await message.answer("Подождите генерацию графика...")
        curr_code = re.search(r'[A-Z]{3}', message.text).group().upper()
        curr_num = (await functions.get_curr_num(curr_code))[0]['currency_num']
        res = await functions.get_historical_info(curr_num)
        dates = []
        rates = []

        for row in res:
            dates.append(await functions.get_time(row["date"], "str"))
            rates.append(float(row["rate"]))

        image = await functions.get_graph(dates,rates,res[0]["unit"],curr_code)

        await message.answer_photo(
            photo=image,
            caption=f"График курса {curr_code}"
        )

    if current_state in (states.CurrState.view, states.CurrState.subs, states.CurrState.unsubs, states.CurrState.graph):
        await state.clear()


    match = re.fullmatch(r'/subscribe([A-Za-z]{3})',message.text)

    if match:
        curr_code = match.group(1).upper()
        curr_num = (await functions.get_curr_num(curr_code))[0]['currency_num']
        res = await functions.check_subscription(message.from_user.id,curr_num)
        res1 = await functions.check_subscription(message.from_user.id,'410')
        print(res)
        #print(res1)
        if res: #if subscription exist
            curr_name = (await functions.get_curr_name(curr_num))[0]['currency_name']
            await message.answer(f"Вы уже подписаны на валюту {curr_code}, {curr_name}!\n\n"
                                    f"Больше информации о валюте:\n"
                                    f"/{curr_code}  ИЛИ  {curr_code.upper()}")
        else:
            curr_name = (await functions.get_curr_name(curr_num))[0]['currency_name']
            await functions.new_subscription(message.from_user.id, curr_num)
            await message.answer(f"Вы успешно подписались на валюту {curr_code}, {curr_name}!")

        #await message.answer(f"{message.from_user.id}, {curr_code}")

    
    match = re.fullmatch(r'/unsubscribe([A-Za-z]{3})',message.text)
    if match:
        curr_code = match.group(1).upper()
        curr_num = (await functions.get_curr_num(curr_code))[0]['currency_num']
        res = await functions.check_subscription(message.from_user.id,curr_num)
        if res:
            await functions.unsubcribe(message.from_user.id, curr_num)
            await message.answer(f"Вы успешно отписались от валюты ({curr_code})!")
        else:
            await message.answer(f"Вы не были подписаны на эту валюту ({curr_code})!")




