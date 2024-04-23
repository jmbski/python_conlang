import json
import logging, logging.config, inspect
from flask import Flask, request, Response, g
from flask_cors import CORS
from random import randint
from modules.custom_logging import loggable, loggable_request
#from modules.log_config import *

from modules import (
    common,
    html_service,
    lexicon,
    log_config,
    utils,
)


# creating the Flask application
app = Flask(__name__)

CORS(app, resources={r"/services/*": {"origins": "*"}})

common.GLOBAL_VARS.initialized = False

@app.before_request
def before_request():
    if(not common.GLOBAL_VARS.initialized):
        for prop in globals().values():
            if(inspect.isfunction(prop)):
                print(prop.__dict__)
        common.GLOBAL_VARS.initialized = True
        
    utils.gen_uow_id()
    g.params = utils.parse_request_data(request)
    

@loggable_request(app, "/services/test", log_level=logging.WARNING)   
#@loggable()
def test_data():
    utils.test_request()
    request_data = g.params
    request_data['UOW_ID'] = g.identifier
    return Response(json.dumps(request_data, indent=4), mimetype='application/json')

@app.route('/services/get-lexicon', methods=['GET'])   
@loggable()
def get_lexicon():
    request_data = utils.parse_request_data(request)
    as_html = request_data.get('as_html', False)
    data = lexicon.load_lexicon_entries()
    data = utils.to_dict(data)
        
    if(as_html):
        data = html_service.get_json_page(data)
        return Response(data, mimetype='text/html')
        
    return Response(json.dumps(data), mimetype='application/json')

@app.route('/services/get-word-bank', methods=['GET'])   
@loggable()
def get_word_bank():
    data = utils.load_data('word_bank.json')
    
    return Response(json.dumps(data), mimetype='application/json')

@app.route('/services/get-lang-configs', methods=['GET', 'POST'])   
@loggable()
def get_lang_configs():
    data = utils.load_data('language_configs.json')
    
    return Response(json.dumps(data), mimetype='application/json')

@app.route('/services/get-words', methods=['GET', 'POST'])   
@loggable()
def get_words():
    word_bank = utils.load_data('word_bank.json', list)
    request_data = utils.parse_request_data(request)
    amount = request_data.get('amount', 50)
    
    words = []
    for i in range(amount):
        rand_index = randint(0, len(word_bank) - 1)
        words.append(word_bank[rand_index])
    
    return Response(json.dumps(words), mimetype='application/json')

if(not common.GLOBAL_VARS.is_gunicorn):
    logging.config.dictConfig(log_config.logconfig_dict) 
