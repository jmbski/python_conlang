from ast import FunctionType
import inspect, json
import ety, uuid
from ety.word import Word
from modules import common, decorators
import sys
import logging, traceback
lj_words = common.LEIPZIG_JAKARTA[0:10]

test_obj = {
    'var1': 1,
    'var2': 2,
    'var3': 3

}

var1 = test_obj.pop('var1')
print(var1, test_obj)
