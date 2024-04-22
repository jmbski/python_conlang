import logging
from modules.custom_logger import CustomLogHandler, CustomLogger
from modules.common import LOG_CONFIG


logging.custom_handler = CustomLogHandler
logging.CustomLogger = CustomLogger

reload = True
logconfig_dict = LOG_CONFIG