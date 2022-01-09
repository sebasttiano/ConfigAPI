#
from configparser import RawConfigParser
import os
import logging

__version__ = '0.0.1'
__all_func__ = ["/devices", "/status", "/execute"]


PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))
DB_URL = 'mysql+pymysql://root:@127.0.0.1:7501/network'

# Loading config
config = RawConfigParser()
config.read([os.path.join(PROJECT_DIR, "../config.ini")])


class ApiLogHandler(logging.Handler):
    '''This is a handler that writes logs to a file'''
    def __init__(self, filename: str):
        logging.Handler.__init__(self)
        self.filename = filename

    def emit(self, record):
        '''This method directly performs the action with the log. The LogRecord object is passed to it'''
        message = self.format(record)
        with open(self.filename, 'a') as file:
            file.write(message + '\n')


# Module logging config
logger_config = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'std_format': {
            'format': '{asctime} - {levelname} - {name} - {message}',
            'style': '{'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'std_format',
        },
        'filesave': {
            # Class init
            '()': ApiLogHandler,
            'level': 'DEBUG',
            'filename': '/var/log/configapi/api.log',
            'formatter': 'std_format'
        }
    },
    'loggers': {
        'CApi': {
            'level': 'DEBUG',
            'handlers': ['console', 'filesave']
        }
    }
}


