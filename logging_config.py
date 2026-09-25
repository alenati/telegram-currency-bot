import logging 
from pathlib import Path 
from datetime import datetime 
from dotenv import load_dotenv
import os 


def setup_logger():
    load_dotenv()

    if os.getenv("LOGS","true").lower() == "true" or os.getenv("LOGS").lower() not in ["true", "false"]:
        Path("logs").mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%d%m%Y-%H%M%S")
        log_file = f"logs/{timestamp}.log"
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            handlers=[
                logging.FileHandler(log_file, encoding="utf-8"),
                logging.StreamHandler(),
            ],
        )
    elif os.getenv("LOGS").lower() == "false":
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        )
    

       

    # logger = logging.getLogger(__name__)

    # logger.info("Application started")
# setup_logger()