from pymongo import MongoClient
from config import client_uri, db_name, collection_name
from config import news_api_key, news_url
import asyncio
from datetime import timedelta, datetime
import requests
import pytz
from io import BytesIO
from googletrans import Translator
from aiogram.types import BufferedInputFile

client = MongoClient(client_uri)
db = client[db_name]
collection = db[collection_name]

translator = Translator()


async def delete_non_relevant():
    trash = datetime.now()-timedelta(days=30)
    collection.delete_many({"date": {"$lt": trash}})


async def get_last_news(date):
    print(list(collection.find({"date": date})))

async def get_and_update():
    await delete_non_relevant()
    parameters = {"category": "business", "apiKey": news_api_key}

    response = requests.get(news_url, parameters)
    data = response.json()
    n = 5
    
    for i in range(n):
        try:
            published_raw = data["articles"][i]["publishedAt"]  
            publishedAt = datetime.fromisoformat(
                published_raw.replace("Z", "+00:00")
            )

            moscow_tz = pytz.timezone('Europe/Moscow')
            now = datetime.now(moscow_tz).date()
            date = datetime(
                now.year,
                now.month,
                now.day
            )

            doc = {
                "author": str(data["articles"][i]["author"]),
                "title": data["articles"][i]["title"],
                "description": data["articles"][i]["description"],
                "url": data["articles"][i]["url"],
                "urlToImage": data["articles"][i]["urlToImage"],
                "publishedAt": publishedAt,
                "content": data["articles"][i]["content"],
                "date": date
            }

            result = collection.update_one(
                {"url": doc["url"]},  
                {"$set": doc},         
                upsert=True            
            )
            

        except Exception as e:
            print(e)
            break
        

# lang = ru, en
# format = inline, txt
async def get_today_news(day: datetime, lang, format):
    txt = ""
    news = list(collection.find({"date": day}))
    if lang == "ru":
        if format == "inline":
            for i in range(len(news)):
                
                tr = await translator.translate(news[i]["title"], dest="ru")
                txt += f'Название статьи:\n{tr.text}\nСсылка:\n{news[i]["url"]}\n\n'
        if format == "txt":
            text = "hello br0"
            buffer = BytesIO()
            buffer.write(text.encode("utf-8"))
            buffer.seek(0)

            file = BufferedInputFile(
                buffer.read(),
                filename="news.txt"
            )

            await message.answer_document(file)

    elif lang == "en":
        if format == "inline":
            for i in range(len(news)):
                txt += f'Название статьи:\n{news[i]["title"]}\nСсылка:\n{news[i]["url"]}\n\n'
        if format == "txt":
            pass 
    return txt
    

# format = json, txt
# lang = ru, en
async def last_month_news():
    pass

# lang = ru, en
async def random_news():
    pass


# async def main():
#     await get_today_news(datetime(2026,1,6), "ru")
#     await get_and_update()

# asyncio.run(main())

