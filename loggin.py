import os
import logging
from config.settings import LOGGING_CONFIG

class Logger:
    def __init__(self, loggername: str):
        self.loggername = loggername

    def getLogger(self):
        logging.config.dictConfig(LOGGING_CONFIG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler = logging.FileHandler('logs/bot.log')
        file_handler.setFormatter(formatter)
        log = logging.getLogger(self.loggername)
        file_handler.flush = lambda: file_handler.stream.flush()
        log.info(f"Logger: {self.loggername} initialized")

        return log



