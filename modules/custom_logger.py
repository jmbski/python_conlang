import logging, sys, uuid
from gunicorn import glogging
from flask import g, has_request_context, has_app_context
    
logging._Logger = logging.Logger
logging._root = logging.root
logging._RootLogger = logging.RootLogger
logging._info = logging.info
logging._warning = logging.warning
logging._error = logging.error
logging._debug = logging.debug
logging._critical = logging.critical
logging._log = logging.log
logging._exception = logging.exception

def info(msg, *args, **kwargs):
    if(has_request_context() or has_app_context()):
        msg = f"{g.get('uow_id')} - {msg}"
        print('\nHASCONTEXT\n')
    print('\nNEW INFO FUNCT\n')
    logging._info(msg, *args, **kwargs)
logging.info = info

class CustomLogger(glogging.Logger):
    def __init__(self, cfg):
        super().__init__(cfg)
        self.uow_id = str(uuid.uuid4())
        
    def critical(self, msg, *args, **kwargs):
        super().critical(f"{self.uow_id} - {msg}", *args, **kwargs)
        
    def error(self, msg, *args, **kwargs):
        super().error(f"{self.uow_id} - {msg}", *args, **kwargs)
        
    def warning(self, msg, *args, **kwargs):
        super().warning(f"{self.uow_id} - {msg}", *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        print('\nCUSTOM LOGGER\n')
        logging.info(f"{self.uow_id} - {msg}", *args, **kwargs)
        
    def debug(self, msg, *args, **kwargs):
        super().debug(f"{self.uow_id} - {msg}", *args, **kwargs)
        
    def exception(self, msg, *args, **kwargs):
        super().exception(f"{self.uow_id} - {msg}", *args, **kwargs)
        
    def log(self, level, msg, *args, **kwargs):
        super().log(level, f"{self.uow_id} - {msg}", *args, **kwargs)

    # add methods for debug, warning, error, etc.
logger_class = 'modules.custom_logger.CustomLogger'
class CustomLogHandler(logging.Handler):
    """
    A handler class which writes logging records, appropriately formatted,
    to a stream. Note that this class does not close the stream, as
    sys.stdout or sys.stderr may be used.
    """

    terminator = '\n'

    def __init__(self, stream=None):
        """
        Initialize the handler.

        If stream is not specified, sys.stderr is used.
        """
        logging.Handler.__init__(self)
        if stream is None:
            stream = sys.stderr
        self.stream = stream

    def flush(self):
        """
        Flushes the stream.
        """
        self.acquire()
        try:
            if self.stream and hasattr(self.stream, "flush"):
                self.stream.flush()
        finally:
            self.release()

    def emit(self, record):
        """
        Emit a record.

        If a formatter is specified, it is used to format the record.
        The record is then written to the stream with a trailing newline.  If
        exception information is present, it is formatted using
        traceback.print_exception and appended to the stream.  If the stream
        has an 'encoding' attribute, it is used to determine how to do the
        output to the stream.
        """
        try:
            """ if(has_app_context()):
                print('UOW', g.get('uow_id'))
                record.uuid = g.get('uow_id') """
                
            if(not hasattr(record, 'uuid')):
                print('no UUID, adding')
                record.uuid = str(uuid.uuid4())
            msg = self.format(record)
            stream = self.stream
            # issue 35046: merged two stream.writes into one.
            stream.write(msg + self.terminator)
            self.flush()
        except RecursionError:  # See issue 36272
            raise
        except Exception as inst:
            print('ERROR: ', inst)
            self.handleError(record)

    def setStream(self, stream):
        """
        Sets the StreamHandler's stream to the specified value,
        if it is different.

        Returns the old stream, if the stream was changed, or None
        if it wasn't.
        """
        if stream is self.stream:
            result = None
        else:
            result = self.stream
            self.acquire()
            try:
                self.flush()
                self.stream = stream
            finally:
                self.release()
        return result

    def __repr__(self):
        level = logging.getLevelName(self.level)
        name = getattr(self.stream, 'name', '')
        #  bpo-36015: name can be an int
        name = str(name)
        if name:
            name += ' '
        return '<%s %s(%s)>' % (self.__class__.__name__, name, level)

    __class_getitem__ = classmethod(logging.GenericAlias)