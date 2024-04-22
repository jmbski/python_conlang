from ast import FunctionType
import inspect, json
import ety, uuid
from ety.word import Word
from modules import common, decorators
import sys
import logging, traceback
lj_words = common.LEIPZIG_JAKARTA[0:10]


def test_function(value: int) -> int:
    new_value = value + 5
    print(new_value)
    new_value = test_function_2(new_value)
    return new_value
    
def test_function_2(value: int) -> int:
    new_value = value + 10
    print(new_value)
    new_value = test_function_3(new_value)
    return new_value

def test_function_3(value: int) -> int:
    new_value = value + 15
    print(new_value)
    new_value = test_function_4(new_value)
    return new_value

def test_function_4(value: int) -> int:
    new_value = value + 20
    print(new_value)
    tb = traceback.extract_stack()
    print(tb)
    return new_value

print('uuid1',uuid.uuid1())
print('uuid1.hex',uuid.uuid1().hex)
print('uuid3',uuid.uuid3(uuid.NAMESPACE_DNS, 'python.org'))
print('uuid3.hex',uuid.uuid3(uuid.NAMESPACE_DNS, 'python.org').hex)
print('uuid4',uuid.uuid4())
print('uuid4.hex',uuid.uuid4().hex)
print('uuid5',uuid.uuid5(uuid.NAMESPACE_DNS, 'python.org'))
print('uuid5.hex',uuid.uuid5(uuid.NAMESPACE_DNS, 'python.org').hex)
