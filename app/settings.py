""" Various settings are stored here """

from configparser import RawConfigParser
import os
import logging

__version__ = '0.0.2'
__all_func__ = ["/devices", "/status", "/execute"]


project_dir = os.path.dirname(os.path.realpath(__file__))
db_url = os.environ.get("MYSQL_URL", "mysql+pymysql://root:@localhost:3306/network")
broker_url = os.environ.get("CELERY_BROKER_URL", "amqp://guest:guest@localhost:5672/")
result_backend = os.environ.get("CELERY_RESULT_BACKEND", "rpc://")


# Loading config
config = RawConfigParser()
config.read([os.path.join(project_dir, "../config.ini"),
             os.path.join(project_dir, "config.ini")])


class ApiLogHandler(logging.Handler):
    """ This is a handler that writes logs to a file """

    def __init__(self, filename: str):
        logging.Handler.__init__(self)
        self.filename = filename

    def emit(self, record):
        """
        This method directly performs the action with the log.
        The LogRecord object is passed to it
        """

        message = self.format(record)
        with open(self.filename, "a", encoding="utf-8") as file:
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
            'filename': '/var/log/confapi/api.log',
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
