import os
import logging
from config.settings import LOGGING_CONFIG

class Logger:
    def __init__(self, loggername: str):
        self.loggername = loggername

    def getLogger(self):
        logging.config.dictConfig(LOGGING_CONFIG)
        log = logging.getLogger(self.loggername)
        log.info(f"Logger: {self.loggername} initialized")

        return log



