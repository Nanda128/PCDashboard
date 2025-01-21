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
        
        logging_level = config.get("logging", "Extensive")
        level_mapping = {
            "Extensive": logging.DEBUG,
            "WarningsOnly": logging.WARNING,
            "ErrorsOnly": logging.ERROR,
            "Mute": logging.CRITICAL + 1
        }
        level = level_mapping.get(logging_level, logging.DEBUG)
        
        for handler in logging.root.handlers:
            handler.setLevel(level)
        
        self.logger = logging.getLogger()
        self.logger.log(logging.INFO, 'Logger initialized with level: {}'.format(logging_level))

    def get_logger(self):
        caller_frame = inspect.stack()[1]
        module = inspect.getmodule(caller_frame[0])
        logger_name = module.__name__ if module else None
        return logging.getLogger(logger_name)
