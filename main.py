import os, json, sys
from modules import (
    common,
    local_ai,
)
from modules.lang_config import LanguageConfig
from nltk.corpus import swadesh, wordnet
from data_builder import db_utils, lang_tools, entities
from warskald import utils, AttrDict, GLOBALS
from sqlalchemy import update
from data_builder.entities import ConlangWord, conlang_defs
#from PyDictionary import PyDictionary

GLOBALS.DATA_PATH = '/home/joseph/coding_base/silverlight/conlang/python/data/'

somevalue = 5
def get_lang(lang_name: str) -> LanguageConfig:
    settings_path = os.path.abspath('./data/language_configs.json')
    
    if(os.path.exists(settings_path)):
        with open(settings_path, 'r') as json_data:
            settings = json.load(json_data)
            lang_config = settings.get(lang_name, {})
            if(lang_config):
                return LanguageConfig(lang_config)

def main():
    base_words = swadesh.words('en')
    for word in common.LEIPZIG_JAKARTA:
        if(word not in base_words):
            base_words.append(word)
            
    base_words.sort()
    """ py_dict = PyDictionary()
    for word in base_words[0:10]:
        print(f"{word}: {py_dict.meaning(word)}") """
def gen_save_word():
    config = db_utils.get_lang_config(1)
    lang = LanguageConfig(config.to_json())
    db_session = db_utils.get_session()
    word, word_ipa = lang.generate_word()
    db_utils.save_conlang_word(word, word_ipa, lang.lang_config_id, db_session)
    db_utils.close_session(db_session, True)
    print(f'Generated word: {word}')

def add_synset(word: str = 'fire', idx: int = 0):
    synsets = lang_tools.get_synsets_json(word)
    db_session = db_utils.get_session()
    for synset in synsets:
        db_utils.save_synset(synset, db_session)
    db_utils.close_session(db_session, True)
    
def save_association():
    db_session = db_utils.get_session()
    
    synsets = db_utils.get_synsets(db_session)
    synset = utils.find_item(synsets, lambda x: not x.conlang_words)
    
    words = db_utils.get_lang_words(1, db_session)
    conlang_word = utils.find_item(words, lambda x: not x.synsets)
    
    #conlang_word = db_utils.get_conlang_word(1, 1, db_session)
    db_utils.associate_conlang_synset(conlang_word, synset, db_session)
    db_utils.close_session(db_session, True)
    
def lex_test():
    lexicon = db_utils.get_lexicon(1)
    if(isinstance(lexicon, list)):
        lexicon = [ word.to_json() for word in lexicon ]
    utils.save_data(lexicon, 'test_lex.json')
    
if __name__ == "__main__":
    args = utils.get_inputs()
    action = args.a or args.action
    synset = AttrDict(db_utils.get_synset(1).to_json())
    lang_configs = utils.load_data('language_configs.json')
    lang_configs = list(lang_configs.values())#[ AttrDict(lang_config) for lang_config in lang_configs.values() ]
    for i, lang_config in enumerate(lang_configs):
        lang_configs[i]['lang_config_id'] = i + 1
        lang_configs[i]['debug'] = False
        
    session = db_utils.get_session()
    
    #db_utils.save_lang_config(lang_configs[0], session)
    db_utils.close_session(session, True)
    if(action == 'add'):
        add_synset(args.w)
    elif(action == 'gen'):
        count = int(args.c) if args.c else 5
        for i in range(count):
            gen_save_word()
    elif(action == 'assoc'):
        save_association()
    else:
        pass#lex_test()