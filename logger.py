import logging
from datetime import datetime
import os

LOG_FILE = f"{datetime.now().strftime('%d_%m_%y_%H_%M_%S')}.log"

LOG_PATH = os.path.join(os.getcwd(), 'log', LOG_FILE)

os.makedirs(LOG_PATH, exist_ok=True)

LOG_FILE_PATH = os.path.join(LOG_PATH, LOG_FILE)

logging.basicConfig(filename=LOG_FILE_PATH,level=logging.INFO,format="[ %(asctime)s ] - %(name)s - %(levelname)s - %(message)s")
