import json
import logging, logging.config, inspect
from data_builder import lang_tools, db_utils
from flask import Flask, request, Response, g, make_response, current_app
import threading
from flask_cors import CORS
from random import randint
#from modules.custom_logging import loggable, loggable_request
from modules.lang_config import LanguageConfig
from modules.cust_threads import CustThread
from concurrent.futures import ThreadPoolExecutor
from warskald import GLOBALS, utils, req_utils, AttrDict

from data_builder.entities import LangConfig
from modules import (
    common,
    html_service,
    lexicon,
    log_config,
)

GLOBALS.DATA_PATH = '/home/joseph/coding_base/silverlight/conlang/python/data/'

LJ_WORDS = utils.load_data('leipzig-jakarta.json')
SWADESH_WORDS = utils.load_data('swadesh_en.json')
COMBINED = list(set(LJ_WORDS + SWADESH_WORDS))

# creating the Flask application
app = Flask(__name__)

CORS(app, resources={r"/services/*": {"origins": "*"}})

common.GLOBAL_VARS.initialized = False

@app.before_request
def before_request():
    g.some_data = {'test': 'test'}
    if(request.method == 'GET'):    
        req_utils.parse_request_data()
    
def some_task(arg1: str, arg2: str, *args):
    obj = {}
    thread: CustThread = threading.current_thread()
    thread.logger.info('Test log message in thread')
    thread.logger.info(thread.g.some_data)
    
    for i in range(0,10000):
        obj[f'{arg1}_{arg2}_{i}'] = randint(0, 100)
    return obj

@app.route('/services/test', methods=['GET', 'POST'])
def test():
    executor = ThreadPoolExecutor()
    thread = threading.current_thread()
    current_app.logger.info(f'Thread has logger: {hasattr(thread, "logger")}')
    current_app.logger.info('Test log message in request')
    future = executor.submit(some_task, 'arg1', 'arg2')
    result = future.result()
    
    
    return Response(json.dumps(result), mimetype='application/json')    
    

@app.route('/services/get-lang-configs', methods=['GET', 'POST'])  
def get_lang_configs():
    configs = db_utils.get_lang_configs()
    
    return Response(json.dumps(configs), mimetype='application/json')

@app.route('/services/get-synsets', methods=['GET', 'POST'])
def get_synsets():
    request_data = g.params
    word = request_data.word or request_data.w
    synset_json = lang_tools.get_synsets_json(word)
    
    return Response(json.dumps(synset_json, indent=4), mimetype='application/json')

@app.route('/services/get-base-words', methods=['GET', 'POST'])
def get_base_words():
    return Response(json.dumps(COMBINED), mimetype='application/json')

@app.route('/services/gen-conlang-word', methods=['GET', 'POST'])
def gen_conlang_word():
    params = g.params
    resp = {}
    lang_config_id = params.langConfigId
    db_session = db_utils.get_session()
    lang_config_data = db_utils.get_lang_config(lang_config_id, db_session)
    if(isinstance(lang_config_data, LangConfig)):
        lang_config_data = lang_config_data.to_json()
    if(isinstance(lang_config_data, dict)):
        lang_config: LanguageConfig = LanguageConfig(lang_config_data)
        
        syllables = params.syllables
        minimum = params.minimum
        maximum = params.maximum
        
        word, ipa = lang_config.generate_word(syllables, minimum, maximum)
        resp = {
            'word': word,
            'ipa': ipa
        }
    db_session.close()
    return Response(json.dumps(resp), mimetype='application/json')
        
@app.route('/services/gen-conlang-words', methods=['GET', 'POST'])
def gen_conlang_words():
    params = g.params
    lang_config_id = params.langConfigId
    
    db_session = db_utils.get_session()
    lang_config_data = db_utils.get_lang_config(lang_config_id, db_session)
    db_session.close()
    
    response = []
    if(isinstance(lang_config_data, LangConfig)):
        lang_config = lang_config.to_json()
    if(isinstance(lang_config_data, dict)):
        lang_config: LanguageConfig = LanguageConfig(lang_config_data)
        
        count = params.count
        syllables = params.syllables
        minimum = params.minimum
        maximum = params.maximum
        
        response = lang_config.generate_words(count, syllables, minimum, maximum)
        
    return Response(json.dumps(response), mimetype='application/json')

@app.route('/services/save-conlang-word', methods=['GET', 'POST'])
def save_conlang_word():
    word = g.params.word
    ipa = g.params.ipa
    lang_config_id = g.params.langConfigId
    db_session = db_utils.get_session()
    db_utils.save_conlang_word(word, ipa, lang_config_id, db_session)
    db_utils.close_session(db_session, True)
    
    return Response(json.dumps({}), mimetype='application/json')

@app.route('/services/save-conlang-words', methods=['GET', 'POST'])
def save_conlang_words():
    words = g.params.words
    word_ipas = g.params.wordIPAs
    lang_config_id = g.params.langConfigId
    
    db_session = db_utils.get_session()
    
    if(len(words) == len(word_ipas)):
        for i, word in enumerate(words):
            db_utils.save_conlang_word(word, word_ipas[i], lang_config_id, db_session)
    db_utils.close_session(db_session, True)
    
    return Response(json.dumps({}), mimetype='application/json')

@app.route('/services/get-lang-words', methods=['GET', 'POST'])
def get_lang_words():
    lang_config_id = g.params.langConfigId
    unused_only = g.params.unusedOnly
    db_session = db_utils.get_session()
    lang_words = db_utils.get_lang_words(lang_config_id, db_session)
    
    if(isinstance(lang_words, list)):
        if(unused_only):
            lang_words = [ word for word in lang_words if not word.synsets ]
        lang_words = [ word.to_json() for word in lang_words ]
        
    db_session.close()
    
    return Response(json.dumps(lang_words), mimetype='application/json')

@app.route('/services/get-lexicon', methods=['GET', 'POST'])
def get_lexicon():
    params = g.params
    lang_config_id = params.langConfigId
    lexicon = db_utils.get_lexicon(lang_config_id)
    if(isinstance(lexicon, list)):
        lexicon = [ word.to_json() for word in lexicon ]
    return Response(json.dumps(lexicon), mimetype='application/json')

@app.route('/services/save-synsets', methods=['GET', 'POST'])
def save_synsets():
    synsets = request.get_json()
    if(isinstance(synsets, list)):
        synsets = [ AttrDict(synset) for synset in synsets ]
        db_session = db_utils.get_session()
        for synset in synsets:
            db_utils.save_synset(synset, db_session)
        db_utils.close_session(db_session, True)
    
        return Response(json.dumps({'status': 'success'}), mimetype='application/json')
    
@app.route('/services/save-lex-entry', methods=['GET', 'POST'])
def save_lex_entry():
    params = AttrDict(request.get_json())
    
    word = params.conlangWord
    synset = params.synset
    
    db_session = db_utils.get_session()
    db_word = db_utils.save_conlang_word(word, db_session)
    db_synset = db_utils.save_synset(synset, db_session)
    
    if(db_word and db_synset):
        db_utils.associate_conlang_synset(db_word, db_synset, db_session)
        
    db_utils.close_session(db_session, True)
    
    return Response(json.dumps({'status': 'success'}), mimetype='application/json')

@app.route('/services/save-lang-config', methods=['GET', 'POST'])
def save_lang_config():
    
    params = request.get_json()
    db_session = db_utils.get_session()
    db_utils.save_lang_config(params, db_session)
    db_utils.close_session(db_session, True)
    
    return Response(json.dumps({'status': 'success'}), mimetype='application/json')
    
if(__name__ == '__main__'):
    app.run(port=5000, debug=True)