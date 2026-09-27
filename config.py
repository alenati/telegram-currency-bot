from dotenv import load_dotenv
import os 

load_dotenv()

class Config:
    PG_HOST= os.getenv("PG_HOST")
    PG_USER= os.getenv("PG_USER")
    PG_PASSWORD= os.getenv("PG_PASSWORD")
    PG_DB_NAME= os.getenv("PG_DB_NAME")

    NEWS_API_KEY= os.getenv("NEWS_API_KEY")
    NEWS_URL=os.getenv("NEWS_URL")

    MG_COLLECTION_NAME=os.getenv("MG_COLLECTION_NAME")
    MG_CLIENT_URI= os.getenv("MG_CLIENT_URI")

    TG_API_KEY= os.getenv("TG_API_KEY")

    LANGUAGE=os.getenv("LANGUAGE")

    LOGS=os.getenv("LOGS")

    RETRIES=os.getenv("RETRIES")

config = Config()