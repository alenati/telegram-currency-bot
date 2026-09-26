from aiogram import Router
from aiogram.filters import Command
from aiogram import types
from aiogram import F
from aiogram.fsm.context import FSMContext
import states
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import functions


router_news = Router()




@router_news.message(F.text.in_(["Сегодня","По дате", "Все за месяц", "Рандомная новость"]))   
async def period_choice(message:types.Message, state: FSMContext):
    if message.text == "Сегодня":
        await state.set_state(states.CurrState.today_news)
        await state.update_data(period = "today")
    elif message.text == "По дате":
        await state.set_state(states.CurrState.date_news)
        await state.update_data(period = "date")
    elif message.text == "Все за месяц":
        await state.set_state(states.CurrState.month_news)
        await state.update_data(period = "month")
    elif message.text == "Рандомная новость":
        await state.set_state(states.CurrState.random_news)
        await state.update_data(period = "random")
    keyboard_lang = ReplyKeyboardMarkup(
        keyboard = [
            [KeyboardButton(text="Русский")],
            [KeyboardButton(text="Английский")]],
        resize_keyboard = True,
        one_time_keyboard = True
        )
    await message.answer("Выбери язык, на котором ты хочешь увидеть новость\n\nВнимание: русский язык создан автоматически, эксперементальный режим.",reply_markup=keyboard_lang)


@router_news.message(F.text.in_(["Русский","Английский"]))   
async def lang_choice(message:types.Message, state: FSMContext):
    
    if message.text == "Русский":
        await state.update_data(lang = "ru")
    elif message.text == "Английский":
        await state.update_data(lang = "en")

    current_state = await state.get_state()

    if current_state == states.CurrState.today_news.state or current_state == states.CurrState.date_news.state:
        keyboard_format = ReplyKeyboardMarkup(
        keyboard = [
            [KeyboardButton(text="Полный обзор статей в .txt")],
            [KeyboardButton(text="Название - Ссылка")]],
        resize_keyboard = True,
        one_time_keyboard = True
        )
        await message.answer("Выбери, в каком формате вывести информацию:", reply_markup = keyboard_format)
    
    elif current_state == states.CurrState.month_news.state:
        #TODO
        await message.answer("Функция пока что не готова:(")
    elif current_state == states.CurrState.random_news.state:
        #TODO
        await message.answer("Функция пока что не готова:(")

@router_news.message(F.text.in_(["Полный обзор статей в .txt","Название - Ссылка"]))   
async def formatting_choice(message:types.Message, state: FSMContext):
    current_state = await state.get_state()
    
    if message.text == "Полный обзор статей в .txt":
        ans = await functions.get_today_news(settings[1], settings[0], "txt")
        await message.answer(ans)
        # text = "hello br0"
        # buffer = BytesIO()
        # buffer.write(text.encode("utf-8"))
        # buffer.seek(0)

        # file = BufferedInputFile(
        #     buffer.read(),
        #     filename="news.txt"
        # )

        # await message.answer_document(file)
    elif message.text == "Название - Ссылка":
        settings = await functions.get_language_and_period(state)
        if settings[1] is not None:
            ans = await functions.get_today_news(settings[1], settings[0], "inline")
            await message.answer(ans)



@router_news.message(Command("news"))
async def news(message: types.Message):

    keyboard_news = ReplyKeyboardMarkup(
    keyboard = [
        [KeyboardButton(text="Сегодня")],
        [KeyboardButton(text="По дате")],
        [KeyboardButton(text="Все за месяц")],
        [KeyboardButton(text="Рандомная новость")]],
    resize_keyboard = True,
    one_time_keyboard = True
    )
    await message.answer("Выбери, за какой период отобразить новости:",reply_markup=keyboard_news)
