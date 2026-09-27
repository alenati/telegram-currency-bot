import json 
from dotenv import load_dotenv
import os 



class Translate:
    def __init__(self):
        load_dotenv()
        lang = os.getenv("LANGUAGE")
        self.lang = lang
    def get(self,json_to_read):
        with open(f"messages/{self.lang}/welcome.json", "r", encoding="utf-8") as f:
            message = json.load(f)
        return (message[json_to_read])



