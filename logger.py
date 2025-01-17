import logging
import logging.config
import json
import os
import inspect
from colorlog import ColoredFormatter

class LoggerManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LoggerManager, cls).__new__(cls)
            cls._instance._initialize_logger()
        return cls._instance

    def _initialize_logger(self):
        if not os.path.exists('logs'):
            os.makedirs('logs')
        with open('config.json', 'r') as f:
            config = json.load(f)
            logging.config.dictConfig(config)
        self.logger = logging.getLogger()
        self.logger.log(logging.INFO, 'Logger initialized')

    def get_logger(self):
        caller_frame = inspect.stack()[1]
        module = inspect.getmodule(caller_frame[0])
        logger_name = module.__name__ if module else None
        return logging.getLogger(logger_name)
