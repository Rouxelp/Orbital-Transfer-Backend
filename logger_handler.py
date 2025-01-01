import logging
import os
from dotenv import load_dotenv

load_dotenv()

# Create a logger
logger = logging.getLogger("HohmannTransfer")
if os.getenv("ENVIRONMENT_VARIABLE_NAME") == "development":
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)

if os.getenv("ENVIRONMENT_VARIABLE_NAME", "").lower() == "prod":
    pass
else:
    # Add a StreamHandler to log to the terminal
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(filename)s - %(funcName)s - %(levelname)s - %(message)s'))
    logger.addHandler(console_handler)

    # Add a FileHandler to log to a file
    file_handler = logging.FileHandler('logfile.txt', mode='w')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(filename)s - %(funcName)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)

# Prevent adding multiple handlers if logger already has handlers
if not logger.hasHandlers():
    logger.addHandler(console_handler)


def handle_logger() -> logging.Logger:
    #* This function is used to handle the logger
    #* For now, it justreturns the logger object
    #* But in the future, it can be used to add more functionality to the logger, to specify it for each use cases in a same job.
    return logger