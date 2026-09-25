import logging 
from pathlib import Path 
from datetime import datetime 

def setup_logger():
    Path("logs").mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%H:%M:%S_%d-%m-%Y")
    log_file = f"logs/{timestamp}.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )
    # logger = logging.getLogger(__name__)

    # logger.info("Application started")
# setup_logger()