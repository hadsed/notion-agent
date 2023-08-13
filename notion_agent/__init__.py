import logging
import os
from dotenv import load_dotenv
load_dotenv()


class config:
    NOTION_API_KEY = os.getenv("NOTION_API_KEY")
    LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", os.getcwd())


def create_logger(
    name: str, 
    create_stream: bool = True, 
    file_name: str = None, 
    level: str = logging.DEBUG
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    formatter = logging.Formatter(
        '%(asctime)s:%(name)s:%(levelname)s:%(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    if file_name:
        file_handler = logging.FileHandler(
            os.path.join(config.LOG_FILE_PATH, file_name))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    if create_stream:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
    return logger


logger = create_logger(__name__, file_name='notion_agent.log')
