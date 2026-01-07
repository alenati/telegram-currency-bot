from pymongo import MongoClient
from config import client_uri, db_name, collection_name
from config import news_api_key, news_url
import asyncio
from datetime import timedelta, datetime
import requests
import pytz

client = MongoClient(client_uri)
db = client[db_name]
collection = db[collection_name]


async def get_last_news(date):
    print(list(collection.find({"date": date})))

async def get_and_update():
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
        
        


async def main():
    await get_and_update()

asyncio.run(main())

