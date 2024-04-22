import json, sys
import logging, logging.config, nanoid
from flask import Flask, request, Response, g
from flask_cors import CORS
from random import randint


from modules import (
    common,
    html_service,
    lexicon,
    utils
)
from modules.common import *

# creating the Flask application
app = Flask(__name__)

CORS(app, resources={r"/services/*": {"origins": "*"}})

@app.before_request
def before_request():
    g.uow_id = nanoid.non_secure_generate('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz', size=10)
    utils.debug_print('before_request', request.endpoint)
    g.params = utils.parse_request_data(request)
    
    
    
@app.route("/services/test")
def test_data():
    print('request', request)
    utils.test_request()
    request_data = g.params#utils.parse_request_data(request)
    request_data['UOW_ID'] = g.uow_id
    return Response(json.dumps(request_data, indent=4), mimetype='application/json')

@app.route('/services/get-lexicon', methods=['GET'])
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
def get_word_bank():
    data = utils.load_data('word_bank.json')
    
    return Response(json.dumps(data), mimetype='application/json')

@app.route('/services/get-lang-configs', methods=['GET', 'POST'])
def get_lang_configs():
    data = utils.load_data('language_configs.json')
    
    return Response(json.dumps(data), mimetype='application/json')

@app.route('/services/get-words', methods=['GET', 'POST'])
def get_words():
    word_bank = utils.load_data('word_bank.json', list)
    request_data = utils.parse_request_data(request)
    amount = request_data.get('amount', 50)
    
    words = []
    for i in range(amount):
        rand_index = randint(0, len(word_bank) - 1)
        words.append(word_bank[rand_index])
    
    return Response(json.dumps(words), mimetype='application/json')

""" logging.config.dictConfig(logconfig_dict)
decorators.log_module_functs(globals()) """
if ('flask' in sys.argv[0].lower()):
    if(common.LOG_CONFIG):
        from modules.custom_logger import CustomLogHandler, CustomLogger
        
        logging.custom_handler = CustomLogHandler
        LOG_CONFIG['formatters']['uuid']['format'] = "[Flask-UUID: %(uuid)s] %(asctime)s [%(module)s] [%(levelname)s] %(message)s"
        logging.config.dictConfig(common.LOG_CONFIG)
        
        logging.RootLogger = CustomLogger
        logging.root = CustomLogger(logging.INFO)
    