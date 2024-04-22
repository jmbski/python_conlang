from typing import Any, Callable
from datetime import datetime
import time, json
from modules import utils

class ProfilerTask:
    funct: Callable = None
    args: list[Any] = []
    kwargs: dict[str, Any] = {}
    start_time: float = None
    end_time: float = None
    elapsed_time: float = None
    function_name: str = None
    funct_result: Any = None
    
    def __init__(self, funct: Callable, *args, **kwargs):
        self.funct = funct
        self.args = args
        self.kwargs = kwargs
        self.function_name = funct.__name__
        
        self.start_time = None
        self.end_time = None
        self.elapsed_time = None
        self.funct_result = None
        
        
    def run_task(self):
        self.start_time = time.time()
        if(callable(self.funct)):
            self.funct_result = self.funct(*self.args, **self.kwargs)
        self.end_time = time.time()
        self.elapsed_time = self.end_time - self.start_time
        return self.to_json()
        
    def to_json(self) -> dict:
        return {
            'function_name': self.function_name,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'elapsed_time': self.elapsed_time,
            'funct_result': self.funct_result
        }
        
class Profiler:
    start_time: float = None
    end_time: float = None
    elapsed_time: float = None
    time_stamp: str = None
    tasks_run: list[str] = []
    task_profiles: list[dict[str, Any]] = []
    task_results: list[Any] = []
    tasks: list[ProfilerTask] = []
    
    def __init__(self, tasks: list[ProfilerTask] | ProfilerTask = None) -> None:
        
        self.time_stamp = datetime.now().strftime('%m/%d/%Y %H:%M:%S')
        
        
        self.start_time = None
        self.end_time = None
        self.elapsed_time = None
        self.tasks_run = []
        self.task_profiles = []
        self.task_results = []
        self.tasks = []
        
        if(isinstance(tasks, list)):
            self.tasks = tasks
        elif(isinstance(tasks, ProfilerTask)):
            self.tasks.append(tasks)
        
    def run_processes(self):
        
        self.time_stamp = datetime.now().strftime('%m/%d/%Y %H:%M:%S')
        self.tasks_run = []
        self.task_profiles = []
        
        self.start_time = time.time()
        
        if(self.tasks):
            for task in self.tasks:
                self.task_profiles.append(task.run_task())
                self.tasks_run.append(task.function_name)
                self.task_results.append(task.funct_result)
            
        self.end_time = time.time()
        self.elapsed_time = self.end_time - self.start_time
        
        return self.to_json()
    
    def add_task(self, funct: Callable, *args, **kwargs):
        self.tasks.append(ProfilerTask(funct, *args, **kwargs))
        
    def get_task_result(self, task_name: str):
        if(task_name in self.tasks_run):
            index = self.tasks_run.index(task_name)
            return self.task_results[index]
        return None
        
    def to_json(self) -> dict:
        return {
            'start_time': self.start_time,
            'end_time': self.end_time,
            'elapsed_time': self.elapsed_time,
            'time_stamp': self.time_stamp,
            'tasks_run': self.tasks_run,
            'task_profiles': self.task_profiles
        }
        
    def to_html_page(self):
        html = utils.load_data('json_page.html')
        html = '\n'.join(html)
        json_data = json.dumps(self.to_json(), indent=4)
        html = html.replace('py_json_data', json_data)
        return html