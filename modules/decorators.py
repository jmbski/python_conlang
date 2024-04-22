from ast import FunctionType
import inspect, json

def loggable_class(cls):
    
    return cls

def loggable(func):
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__} with args {args} and kwargs {kwargs}")
        return_value = func(*args, **kwargs)
        print(f"{func.__name__} returned {return_value}")
        return return_value
    wrapper._loggable = True
    return wrapper

@loggable
def test_funct(value: int) -> int:
    return value + 5

@loggable_class
class TestClass:
    def __init__(self, init: dict = {}) -> None:
        self.var1: int = init.get('var1', 0)
        self.var2: str = init.get('var2', 'default')
        self.var3: list = init.get('var3', [])
        self.var4: dict = init.get('var4', {})
        self.var5: bool = init.get('var5', False)
        
    def __str__(self) -> str:
        return f"{self.var1} {self.var2} {self.var3} {self.var4} {self.var5}"
    
    def test_function(self, value: int) -> int:
        return value + self.var1
    
    
def log_module_functs(_globals: list):
    
    functions_list: list[FunctionType] = [o for o in _globals.values() if inspect.isfunction(o)]
    
    for funct in functions_list:
        if(hasattr(funct, '_loggable')):
            continue
        else:
            wrapped_funct = loggable(funct)
            _globals[funct.__name__] = wrapped_funct