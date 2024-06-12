from concurrent.futures import ThreadPoolExecutor
from flask import g, request, current_app, has_app_context, has_request_context
import threading
from warskald import AttrDict

_OriginalThread = threading.Thread
class CustThread(_OriginalThread):
    def __init__(self, *args, **kwargs):
        self.g = AttrDict(g.__dict__) if has_request_context() else None
        self.request = request if has_request_context() else None
        self.current_app = current_app if has_app_context() else None
        self.logger = current_app.logger if has_app_context() else None
        
        super().__init__(*args, **kwargs)
        
    def run(self):
        super().run()
        
threading.Thread = CustThread

class CustomThreadPoolExecutor(ThreadPoolExecutor):
    def __init__(self, max_workers=None, thread_name_prefix=''):
        self.g = g if has_request_context() else None
        self.request = request if has_request_context() else None
        self.current_app = current_app if has_app_context() else None
        self.logger = current_app.logger if has_app_context() else None
        
        super().__init__(max_workers, thread_name_prefix)
        
    def submit(self, fn, *args, **kwargs):
        some_data = {'test': 'test'}
        args = list(args) + [self.logger, some_data]
        args = tuple(args)
        return super().submit(fn, *args, **kwargs)