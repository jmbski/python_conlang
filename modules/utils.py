import json, nanoid, re, flask
from flask import g, has_request_context, request
from typing import Any
from datetime import datetime
from modules.common import (
    DATA_PATH,
    DOUBLE_QUOTE_PATTERN,
    LIST_STR_PATTERN,
    LIST_STR_SEPARATOR_PATTERN,
    SINGLE_QUOTE_PATTERN,
    GLOBAL_VARS
)
from inspect import isclass
import inspect
from collections import OrderedDict


def stringify_float(value: float):
    return str(value).replace(',','')

def gen_id(size: int = 10) -> int:    
    ID = nanoid.generate(alphabet='0123456789', size=size)
    return int(ID)

def is_numeric(value):
    try:
        if(isinstance(value, str)):
            value = value.replace(',', '')
        float(value)
        return True
    except Exception:
        
        return False
    
def to_dict(obj: Any, allow_none: bool = True, forbidden_keys: list[str] = [], allow_empty: bool = True, 
            forbidden_values: list[Any] = [], forbidden_types: list[type] = (), forbidden_prefixes: list[str] = [],
            strip_prefixes: list = ['_prop_']):
    if(isinstance(obj, list)):
        return [to_dict(item, allow_none, forbidden_keys, allow_empty, forbidden_values, forbidden_types, forbidden_prefixes ) for item in obj]
    if(isinstance(obj, dict)):
        new_dict = {}
        for key, value in obj.items():
            safe_key = str(key)
            if(safe_key in forbidden_keys or key in forbidden_keys):
                continue
            if(value in forbidden_values):
                continue
            if(isinstance(value, forbidden_types)):
                continue
            if(safe_key.startswith(tuple(forbidden_prefixes))):
                continue
            if(value == None and not allow_none):
                continue
            if(not value and value != 0 and not allow_empty):
                continue
            if(strip_prefixes):
                for prefix in strip_prefixes:
                    if(safe_key.startswith(prefix)):
                        safe_key = safe_key[len(prefix):]
                        break
            new_dict[safe_key] = to_dict(value, allow_none, forbidden_keys, allow_empty, forbidden_values, forbidden_types, forbidden_prefixes)
        return new_dict
    if(isinstance(obj, datetime)):
        return obj.strftime('%m/%d/%Y')
    if not isinstance(obj, (str, int, float, list, dict)) and hasattr(obj, "__dict__"):
        return to_dict(obj.__dict__, allow_none, forbidden_keys, allow_empty, forbidden_values, forbidden_types, forbidden_prefixes)
    
    return obj

def save_data(data: Any, filename: str):
    filename = DATA_PATH + filename
    as_json = filename.endswith('.json') and isinstance(data, (list, dict))
    
    if(as_json):
        with open(filename, 'w') as writer:
            data = to_dict(data)
            writer.write(json.dumps(data, indent=4, ensure_ascii=False))
    else:
        with open(filename, 'w') as writer:
            writer.write(data)
            
def load_data(filename: str, as_type: type = None) -> list | dict | str | None:
    filename = DATA_PATH + filename
    
    if(filename.endswith('.json')):
        with open(filename, 'r') as reader:
            if(as_type):
                return as_type(json.load(reader))
            return json.load(reader)
    else:
        with open(filename, 'r') as reader:
            return reader.readlines()
        

        
def parse_str_type(value: str, empty_value: Any = 0):
    if(isinstance(value, str)):
        if(re.search(DOUBLE_QUOTE_PATTERN, value)):
            return value.strip().strip('"')
        
        if(re.search(SINGLE_QUOTE_PATTERN, value)):
            return value.strip().strip("'")
        
        if(re.search(LIST_STR_PATTERN, value)):
            return list_str_to_list(value)
        
        value = value.strip().replace(',', '')
        
        if(is_numeric(value)):
            if('.' in value):
                return float(value)
            return int(value)
        
        if(value.lower() == 'true'):
            return True
        
        if(value.lower() == 'false'):
            return False
    
        if(value.strip() == ''):
            return empty_value
        
    return value

def is_dict_list(data: Any):
    if(isinstance(data, list)):
        if(all(isinstance(item, dict) for item in data)):
            return True
    return False

def camel_to_snake_case(string: str):
    if(string == string.upper()):
        return string.lower()
    return ''.join(['_'+i.lower() if i.isupper() else i for i in string]).lstrip('_')

def list_str_to_list(list_str: str):
    search = re.search(LIST_STR_PATTERN, list_str)
    
    if(search):
        parsed_list = []
        list_str = search.group(1)
        
        list_split = list_str.split(',')
        
        for item in list_split:
            parsed_list.append(parse_str_type(item))
            
        return parsed_list
    return list_str

def parse_request_data(request: flask.Request):
    if(isinstance(request, flask.Request)):
        request_data = {}
        
        if(request.method == 'GET'):
            for key, value in request.args.items():
                request_data[key] = parse_str_type(value)
            return request_data
        return request.get_json()
    
def pretty_print(data: Any, newlines: bool = True):
    string = json.dumps(to_dict(data), indent=4, ensure_ascii=False)
    if(newlines):
        string = f'\n{string}\n'
    print(string)

def debug_print(*args):
    strings = list(args)
    strings.insert(0, '\n')
    strings.append('\n')
    print(*strings)
    
def normalize_str(value: str):
    special_chars = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '_', '+', '=', '{', '}', '[', ']', '|', '\\', ':', ';', '"', "'", '<', '>', ',', '.', '?', '/']
    result = value.strip().lower()
    for char in special_chars:
        result = result.replace(char, '')
        
    return value.strip()

def last(arr: list):
    return arr[len(arr) - 1]

def set_nested(obj: dict | list, path: list[str] | str, value: Any, debug: bool = False) -> None:
    if(isinstance(path, str)):
        path = path.split('.')
    
    if(debug):
        debug_print('starting function')
        pretty_print({
            'obj': obj,
            'path': path,
            'value': value
        })
    
    if(len(path) == 1):
        if(isinstance(obj, dict)):
            obj[path[0]] = value
        elif(isinstance(obj, list) and path[0].isdigit()):
            if(int(path[0]) < len(obj)):
                obj[int(path[0])] = value
            else:
                obj.append(value)
                
    else:
        key = path.pop(0)
        
        if(debug): 
            debug_print('key', key)
        
        if(isinstance(obj, list) and key.isdigit()): # true
            if(debug):
                debug_print('obj is list', 'key < len', int(key) < len(obj))
                
            if(int(key) < len(obj)): # 3 < 3 == False
                sub = obj[int(key)]
                if(not sub or not isinstance(sub, (dict, list))):
                    if(debug):
                        debug_print('sub is None or not an object', 'creating new sub')
                        
                    if(path[0].isdigit()):
                        obj[int(key)] = []
                    else:
                        obj[int(key)] = {}
                        
                set_nested(obj[int(key)], path, value)
            else:
                if(debug):
                    debug_print('out of bounds', 'inserting new value', f'path[0] = {path[0]}')
                    
                if(path[0].isdigit()):
                    obj.insert(int(key), [])
                else:
                    obj.insert(int(key), {})
                
                if(debug):
                    debug_print('blank inserted', obj)
                    
                set_nested(last(obj), path, value)
                
        elif(isinstance(obj, dict)):
            sub = obj.get(key)
            
            if(debug):
                debug_print('obj is dict', 'sub:', sub)
                
            if(not sub or not isinstance(sub, (dict, list))):
                if(debug):
                    debug_print('sub is None or not an object', 'creating new sub')
                    
                if(path[0].isdigit()):
                    obj[key] = []
                else:
                    obj[key] = {}
                
                if(debug):
                    debug_print('new sub created', obj)
            
            set_nested(obj.get(key), path, value)
        
def get_nested(obj: dict | list, path: list[str] | str) -> Any:
    if(isinstance(path, str)):
        path = path.split('.')
        
    if(len(path) == 1):
        if(isinstance(obj, dict)):
            return obj.get(path[0])
        elif(isinstance(obj, list) and path[0].isdigit()):
            return obj[int(path[0])]
    else:
        key = path.pop(0)
        if(isinstance(obj, list) and key.isdigit()):
            if(int(key) < len(obj)):
                return get_nested(obj[int(key)], path)
            return None
        if(key not in obj):
            return None
        return get_nested(obj[key], path)
    
def reorder_dict_by_value_len(obj: dict) -> dict:
    return dict(OrderedDict(sorted(obj.items(), key=lambda item: len(item[1]), reverse=True)))

def is_simple_funct(obj: Any) -> bool:
    return callable(obj) and len(inspect.signature(obj).parameters) == 0

def clean_words(words: list[str]) -> list[str]:
    cleaned_words = []
    latin_chars_w_accents = re.compile(r'^[a-zA-ZÀ-ÿ\-\'\’\.\,\_]+?$')
    for word in words:
        if(latin_chars_w_accents.match(word)):
            cleaned_words.append(word)
    return cleaned_words

def reorder_dict_by_value(obj: dict) -> dict:
    return dict(OrderedDict(sorted(obj.items(), key=lambda item: item[1], reverse=True))) 

def test_request():
    if(has_request_context()):
        print('request', g.get('identifier'))

def gen_simple_id(count: int = 10) -> str:
    return nanoid.non_secure_generate('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz', size=count)

def gen_uow_id():
    server = 'gunicorn' if GLOBAL_VARS.is_gunicorn else 'flask'
    req_id = gen_simple_id()
    if(has_request_context() and request is not None):
        endpoint = request.endpoint
        
        g.identifier = f'{server}-{endpoint}-{req_id}'
    else:
        if(GLOBAL_VARS.get('server_id') is None):
            server_id = f'{server}-{req_id}-FLASKAPI'
            GLOBAL_VARS.server_id = server_id
        
        