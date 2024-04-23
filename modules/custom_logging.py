import logging, traceback
from flask import g, has_request_context
from modules.common import GLOBAL_VARS
from modules import utils
from typing import Any, Callable

class CustomLogRecord(logging.LogRecord):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if(has_request_context()):
            self.identifier = g.identifier
        else:
            utils.gen_uow_id()
            self.identifier = GLOBAL_VARS.get('server_id', 'FLASKAPI')

""" def _loggable(funct: Callable[..., Any]) -> Callable[..., Any]:
    def wrapper(*args, **kwargs) -> Any:
        print('logging function')
        logging.log(logging.INFO, f'Function {funct.__name__} called with args: {args} and kwargs: {kwargs}')
        return_val = None
        failed = False
        try:
            return_val = funct(*args, **kwargs)
        except Exception as e:
            logging.error(f'Function {funct.__name__} raised an exception: {e}')
            logging.error(traceback.format_exc())
            failed = True
            
        if(not failed):                
            logging.log(logging.INFO, f'Function {funct.__name__} returned: {return_val}')
        
        return return_val
    return wrapper """
    
def loggable(log_level: int = logging.INFO, use_try_except: bool = True, logger: logging.Logger | str = 'gunicorn.error'):
    if(isinstance(logger, str)):
        logger = logging.getLogger(logger)
        
    def decorator_funct(func: Callable[..., Any]) -> Callable[..., Any]:
        def wrapper(*args, **kwargs) -> Any:
            logging.log(log_level, f'Function {func.__name__} called with args: {args} and kwargs: {kwargs}')
            return_val = None
            failed = False
            if(use_try_except):
                try:
                    return_val = func(*args, **kwargs)
                except Exception as e:
                    logging.error(f'Function {func.__name__} raised an exception: {e}')
                    logging.error(traceback.format_exc())
            else:
                return_val = func(*args, **kwargs)
            
            if(not failed):                
                logging.log(log_level, f'Function {func.__name__} returned: {return_val}')
            
            return return_val
        wrapper.__name__ = func.__name__
        return wrapper
    return decorator_funct

def loggable_request(app, rule: str, **options: Any):
    log_level = options.pop('log_level', logging.INFO)
    use_try_except = options.pop('use_try_except', True)
    logger = options.pop('logger', 'gunicorn.error')
    
    def decorator_funct(funct):
        @app.route(rule, **options)
        def wrapper(*args, **kwargs):
            return loggable(log_level, use_try_except, logger)(funct)(*args, **kwargs)
        
        wrapper.__name__ = funct.__name__
        return wrapper
    return decorator_funct
    