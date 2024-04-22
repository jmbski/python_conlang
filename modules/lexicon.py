from __future__ import annotations
import json, os, inspect
from modules import (
    utils,
    word_gen,
    decorators
)
import nltk, ety
from nltk.corpus import swadesh, wordnet, wordnet_ic
from nltk.corpus.reader.wordnet import WordNetCorpusReader
from nltk.corpus.reader.wordnet import Synset, Lemma
from nltk.stem.porter import PorterStemmer
from nltk.stem import WordNetLemmatizer, SnowballStemmer
from nltk.stem.lancaster import LancasterStemmer

from fuzzywuzzy import fuzz
from modules.common import *
from modules.lang_data import LanguageData
from tqdm import tqdm
from wordsegment import load, segment

class JsonMixin:
    def to_json(self) -> dict:
        return utils.to_dict(self)
    
class LexiconEntry(JsonMixin):
    _prop_word: str = None
    ipa: str = None
    eng_word: str = None
    wn_id: str = None
    definition: str = None
    examples: list[str] = []
    part_of_speech: str = None
    hypernyms: list[LexLink] = []
    hyponyms: list[LexLink] = []
    holonyms: list[LexLink] = []
    meronyms: list[LexLink] = []
    antonyms: list[LexLink] = []
    synonyms: list[LexLink] = []
    similar_to: list[LexLink] = []
    attributes: list[LexLink] = []
    entailments: list[LexLink] = []
    
    
    def __init__(self, init: dict | Synset = None) -> None:
        self.word = ''
        if(isinstance(init, dict)):
            for key, value in init.items():
                if(isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict)):
                    setattr(self, key, [LexLink(item) for item in value])
                setattr(self, key, value)
        elif(isinstance(init, Synset)):
            self.eng_word = synset_name(init)
            self.wn_id = get_wn_id(init)
            self.definition = get_wn_def(init)
            self.examples = init.examples()
            self.part_of_speech = POS.get(init.pos())
            self.hypernyms = get_synset_lexlinks(init, 'hypernyms')
            self.hyponyms = get_synset_lexlinks(init, 'hyponyms')
            self.holonyms = get_synset_lexlinks(init, 'holonyms')
            self.meronyms = get_synset_lexlinks(init, 'meronyms')
            self.antonyms = get_synset_lexlinks(init, 'antonyms')
            self.synonyms = get_synset_lexlinks(init, 'synonyms')
            self.similar_to = get_synset_lexlinks(init, 'similar_to')
            self.attributes = get_synset_lexlinks(init, 'attributes')
            self.entailments = get_synset_lexlinks(init, 'entailments')
                
    @property
    def word(self) -> str:
        return self._prop_word
    
    @word.setter
    def word(self, value: str) -> None:
        self._prop_word = value
        self.ipa = word_gen.grapheme_to_IPA(value)
        
    def get_related_entries(self, existing_list: list[LexiconEntry] = None) -> list[LexiconEntry]:
        if(not existing_list):
            existing_list_copy = [self]
        else:
            existing_list_copy = existing_list.copy()
        
        for prop_name in dir(self):
            if(not prop_name.startswith('_')):
                prop = getattr(self, prop_name)
                if(isinstance(prop, list) and len(prop) > 0 and isinstance(prop[0], LexLink)):
                    for link in prop:
                        if(not in_lex_list(link.wn_id, existing_list_copy)):
                            existing_list_copy.append(LexiconEntry(wordnet.synset(link.wn_id)))
                            #existing_list_copy[-1].get_related_entries(existing_list_copy)
        return existing_list_copy
                
class LexLink(JsonMixin):
    word: str = None
    definition: str = None
    wn_id: str = None
    
    def __init__(self, init: dict | Synset = None) -> None:
        if(isinstance(init, dict)):
            for key, value in init.items():
                setattr(self, key, value)
        elif(isinstance(init, Synset)):
            self.word = synset_name(init)
            self.wn_id = get_wn_id(init)
            self.definition = get_wn_def(init)
    
def save_lexicon_data(data: list[LexiconEntry]):
    with open('./data/lexicon.json', 'w') as writer:
        writer.write(json.dumps([item.to_json() for item in data], indent=4, ensure_ascii=False))
        
def load_lexicon_data() -> list[LexiconEntry]:
    data = utils.load_data('lexicon.json')
    if(utils.is_dict_list(data)):
        return [LexiconEntry(item) for item in data]
    return data

def save_lexicon_entries(data: list[LexiconEntry]):
    with open('./data/lexicon_entries.json', 'w') as writer:
        writer.write(json.dumps([item.to_json() for item in data], indent=4, ensure_ascii=False))
        
def load_lexicon_entries() -> list[LexiconEntry]:
    data = utils.load_data('lexicon_entries.json')
    if(utils.is_dict_list(data)):
        return [LexiconEntry(item) for item in data]
    return data



def process_conworkshop_data():
    data = utils.load_data('dictionary.txt')
    if(isinstance(data, list)):
        entries = load_lexicon_data()
        for line in data:
            entry = line.strip().split(' ')
            
            if(len(entry) >= 3):
                word = entry[0]
                pos = POS.get(entry[1])
                definition = ' '.join(entry[2:])
                synsets = wordnet.synsets(definition, pos)
                lex_links = [ LexLink(synset) for synset in synsets ]
                choices = [ f'{i+1}. {lex_link.word} ({lex_link.definition})' for i, lex_link in enumerate(lex_links) ]
                
                
                print(f'Select which entries to include for {word} ({pos}):')
                for choice in choices:
                    print(choice)
                    
                selection = input('Enter the numbers of the entries to include, separated by commas: ')
                selection = selection.split(',')
                
                if(selection[0] != ''):
                    selected_entries = [ LexiconEntry(synsets[int(i) - 1]) for i in selection ]
                    for selected_entry in selected_entries:
                        if(not in_lex_list(selected_entry.wn_id, entries)):
                            selected_entry.word = word
                            entries.append(selected_entry)
                            related_entries = selected_entry.get_related_entries(entries)
                            num_related = len(related_entries) - len(entries)
                            add_related = input(f'Add {num_related} related entries? (y/n): ')
                            if(add_related.lower() == 'y'):
                                entries = related_entries
                        else:
                            existing_index = next((i for i, item in enumerate(entries) if item.wn_id == selected_entry.wn_id), None)
                            
                            if(existing_index is not None):
                                entries[existing_index].word = word
                                print(f'Entry for {word} - {entries[existing_index].eng_word} already exists. Updating word and related entries.')
                    save_lexicon_data(entries)
                
        #save_lexicon_data(entries)

def combine_lexicons():
    entries = load_lexicon_entries()
    data = load_lexicon_data()
    for entry in data:
        if(not in_lex_list(entry.wn_id, entries)):
            entries.append(entry)
        else:
            existing_index = next((i for i, item in enumerate(entries) if item.wn_id == entry.wn_id), None)
            if(existing_index is not None):
                entries[existing_index] = entry
    save_lexicon_entries(entries)
    
def check_lexicon():
    entries = load_lexicon_entries()
    mapped_entries = [ entry for entry in entries if entry.word != '']
    mapped_words = [ entry.word for entry in mapped_entries ]
    dict_words = get_dictionary_defs()
    unmapped_words = [ word for word in dict_words if word[0] not in mapped_words]
    father_words = search_lexicon(definition='father')
    utils.save_data(father_words, 'lex_test.json')

def fuzzy_search(prop_name: str, value: str, data: list[LexiconEntry], threshold: int = 90) -> list[LexiconEntry]:
    results = []
    for entry in data:
        if(hasattr(entry, prop_name)):
            prop = getattr(entry, prop_name)
            if(isinstance(prop, str)):
                if((fuzz.ratio(value, prop) >= threshold) or value in prop):
                    results.append(entry)
    return results

def search_lexicon(word: str = None, definition: str = None, wn_id: str = None, use_fuzzy: bool = True) -> LexiconEntry | list[LexiconEntry]:
    entries = load_lexicon_entries()
    results = []
    if(word):
        if(use_fuzzy):
            results = fuzzy_search('word', word, entries)
        else:
            results = [ entry for entry in entries if entry.word == word ]
            
    elif(definition):
        if(use_fuzzy):
            results = fuzzy_search('definition', definition, entries)
        else:
            results = [ entry for entry in entries if definition in entry.definition ]
            
    if(wn_id):
        results = [ entry for entry in entries if entry.wn_id == wn_id ]
    
    if(len(results) == 1):
        return results[0]
    return results

def get_dictionary_defs() -> list[tuple[str, str, str]]:
    dictionary_txt = utils.load_data('dictionary.txt')
    dict_words = []
    for line in dictionary_txt:
        if(len(line.strip()) > 0):
            line_split = line.strip().split(' ')
            fs_word = line_split[0]
            pos = line_split[1]
            definition = ' '.join(line_split[2:])
            dict_words.append((fs_word, pos, definition))
            
    return dict_words

def init_nltk():
    for name, path in NLTK_DOWNLOADS.items():
        if(not os.path.exists(path)):
            nltk.download(name, download_dir=NLTK_DATA_DIR)
            
def in_lex_list(wn_id: str, lexlinks: list[LexLink] | list[LexiconEntry]) -> bool:
    if(isinstance(lexlinks, list)):
        for link in lexlinks:
            if(link.wn_id == wn_id):
                return True
    return False

def same_synset(synset1: Synset | Lemma, synset2: Synset | Lemma) -> bool:
    name1 = synset1.name() if isinstance(synset1, Synset) else synset1.synset().name()
    name2 = synset2.name() if isinstance(synset2, Synset) else synset2.synset().name()
    return name1 == name2

def synset_name(wn_object: Synset | Lemma) -> str:
    return wn_object.name().split('.')[0] if isinstance(wn_object, Synset) else wn_object.name()

def get_wn_id(wn_object: Synset | Lemma) -> str:
    return wn_object.name() if isinstance(wn_object, Synset) else wn_object.synset().name()

def get_wn_def(wn_object: Synset | Lemma) -> str:
    return wn_object.definition() if isinstance(wn_object, Synset) else wn_object.synset().definition()

def get_synset_lexlinks(synset: Synset, prop_name: str) -> list[LexLink]:
    links = []
    prop_names = [prop_name]
    if(prop_name == 'holonyms'):
        prop_names = ['member_holonyms', 'part_holonyms', 'substance_holonyms']
    elif(prop_name == 'meronyms'):
        prop_names = ['member_meronyms', 'part_meronyms', 'substance_meronyms']
        
    use_lemmas = prop_name == 'antonyms' or prop_name == 'synonyms'
    search_objs = synset.lemmas() if use_lemmas else [synset]
    
    for search_obj in search_objs:
        for prop_name in prop_names:
            if(hasattr(search_obj, prop_name)):
                for item in getattr(search_obj, prop_name)():
                    if(same_synset(item, synset)):
                        continue
                    if(not in_lex_list(item.name(), links)):
                        links.append(LexLink({
                            'word': synset_name(item),
                            'definition': get_wn_def(item),
                            'wn_id': get_wn_id(item)
                        }))
    return links

def build_lexicon_entries():
    init_nltk()
    
    english_words = swadesh.words('en')
    
    # add words from the Leipzig-Jakarta list that aren't already in the swadesh list
    for word in LEIPZIG_JAKARTA:
        if(word not in english_words):
            english_words.append(word)
    
    definition_list = load_lexicon_entries()
    # Loop through each set
    for word in english_words:
        synsets = wordnet.synsets(word)
        for synset in synsets:
            if(not in_lex_list(get_wn_id(synset), definition_list)):
                lexicon_entry = LexiconEntry(synset)
                definition_list.append(lexicon_entry)
            
    utils.save_data(definition_list, 'lexicon_entries.json')
    
def build_whole_language():
    init_nltk()
    whole_bank: dict = {}
    whole_language: dict[str, LexiconEntry] = {}
    
    words = list(wordnet.words())
    
    def gen_fs_word():
        fs_word, fs_ipa = word_gen.generate_word(minimum=1, maximum=5)
        while(whole_bank.get(fs_word)):
            fs_word, fs_ipa = word_gen.generate_word(minimum=1, maximum=5)
            if(not whole_bank.get(fs_word)):
                whole_bank[fs_word] = fs_ipa
                
        return fs_word
                
    if(len(whole_language.keys()) <= 0):
            
        synsets = list(wordnet.all_synsets())
        for synset in tqdm(synsets):
            whole_language[synset.name()] = LexiconEntry(synset)
                
    for entry in tqdm(whole_language.values()):
        if(not entry.ipa):
            fs_word = gen_fs_word()
            if(fs_word):
                entry.word = fs_word
            
    print(len(whole_language.keys()))
    utils.save_data(whole_language, 'whole_language.json')
    
def test():
    
    lang_settings = {
        'name': 'First Speech',
        'phonetic_inventory': PHONETIC_INVENTORY,
        'orthography_categories': ORTHO_CATEGORIES,
        'orth_syllables': SYLLABLES,
        'grapheme_lookup': GRAPHEME_LOOKUP,
    }
    
    lang = LanguageData(lang_settings)
    
    """ dictionary = utils.load_data('english_dict.json')
    meanings_list = []
    for word, definition in dictionary.items():
        meanings = definition.get('MEANINGS', [])
        for meaning in meanings:
            if(len(meaning) >= 4 and len(meaning[3]) > 0):
                meanings_list.append((word, definition))
    
    
    # ety,                
    utils.pretty_print(meanings_list[10])
    dict_words = { key.lower() for key in dictionary.keys() }
    words = list(wordnet.words())
    words = { word.lower() for word in words }
    
    all_words = dict_words.union(words)
    
    all_words = utils.clean_words(list(all_words)) """
    
    
    
            
    
    """ entries = utils.load_data('whole_language.json')
    entries = list(entries.values())
    def hyponyms(entry: dict):
        return len(entry.get('hyponyms', []))
    
    def meronyms(entry: dict):
        return len(entry.get('meronyms', []))
    
    def hypo_mero(entry: dict):
        return hyponyms(entry) + meronyms(entry)
    
    def hyper_holo(entry: dict):
        return len(entry.get('hypernyms', [])) + len(entry.get('holonyms', []))
    
    simple_words = [ entry.get('eng_word') for entry in entries if hypo_mero(entry) == 0 and hyper_holo(entry) == 0 ]
    print(len(simple_words)) """
decorators.log_module_functs(globals())