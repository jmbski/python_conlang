import logging
from modules.custom_logging import CustomLogRecord
from modules.common import LOG_CONFIG, GLOBAL_VARS
from modules import utils


_server = 'gunicorn' if GLOBAL_VARS.is_gunicorn else 'flask'
_id_str = utils.gen_simple_id()

GLOBAL_VARS.server_id = f'{_server}-{_id_str}-FLASKAPI'

#logging.setLogRecordFactory(CustomLogRecord)

reload = True
logconfig_dict = LOG_CONFIG