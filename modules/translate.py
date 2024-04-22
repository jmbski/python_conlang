from __future__ import annotations
import os, json, re, spacy
import eng_to_ipa
from modules import (
    common,
    lexicon,
    utils,
    word_gen
)

from modules.lexicon import (
    JsonMixin,
    LexiconEntry,
    LexLink,
)

from spacy.tokens.doc import Doc
from spacy.tokens.token import Token
from nltk.corpus import wordnet, stopwords, words, cmudict
from tqdm import tqdm
from phonemizer.phonemize import phonemize
from phonemizer.backend import EspeakBackend
from phonemizer.separator import Separator
from panphon import FeatureTable, featuretable
from scipy.spatial import distance

char_to_int_map = {'+': 1, '-': -1, '0': 0}

ft = FeatureTable()
fs_phonemes = list(common.PHONETIC_INVENTORY.values())
    
def get_phoneme_vector(phoneme: str) -> list[int]:
    target_vector = []
    
    if phoneme in common.IPA_ESCAPE:
        phoneme = common.IPA_ESCAPE[phoneme]
      
    for p in phoneme:
        target_vector_list = ft.word_to_vector_list(p)
        if len(target_vector_list) > 0:
            vector = target_vector_list[0]
            target_vector.extend([char_to_int_map[char] for char in vector])
            
    max_length = 48
    if len(target_vector) < max_length:
        padding = [ 0 for _ in range(max_length - len(target_vector)) ]
        target_vector.extend(padding)
    
    return target_vector
            
fs_vectors = [ get_phoneme_vector(phoneme) for phoneme in fs_phonemes ]

SPACY_POS_TO_WORDNET_POS = {
    "NOUN": "n",
    "VERB": "v",
    "ADJ": "a",
    "ADV": "r",
    "ADP": "s",
    "AUX": "v",
    "PRON": "n",
    "PROPN": "n",
    "NUM": "n",
}

""" INTJ	CCONJ	
	DET	 
	NUM	 
	PART	 
 		 
 	SCONJ """
  
class TokenInfo(JsonMixin):
    text: str = None
    pos: str = None
    wn_ids: list[str] = []
    
    def __init__(self, token: Token) -> None:
        self.text = token.text
        self.pos = token.pos_
        
        synsets = wordnet.synsets(token.text)
        if(synsets):
            self.wn_ids = [synset.name() for synset in synsets]

def graphemize(word: str) -> str:
    
    separator = Separator(phone=' ', word='')
    phonemes = phonemize(word, backend='espeak', separator=separator, language='en-us')
    phonemes = phonemes.strip().split(' ')
    grapheme_word = ''
    
    for phoneme in phonemes:
            
        if(not common.GRAPHEME_LOOKUP.get(phoneme)):
            target_vector = get_phoneme_vector(phoneme)
            
            # Padding the smaller target_vector with zeros
            
                
            distances = [(phon, distance.euclidean(target_vector, vector) ) for phon, vector in zip(fs_phonemes, fs_vectors)]
            match = min(distances, key=lambda x: x[1])
            best_phoneme = match[0]
            grapheme = common.GRAPHEME_LOOKUP[best_phoneme]
        else:
            grapheme = common.GRAPHEME_LOOKUP[phoneme]
            
        grapheme_word += grapheme
        
    return grapheme_word

def clean_words(words: list[str]) -> list[str]:
    cleaned_words = []
    latin_chars_w_accents = re.compile(r'^[a-zA-ZÀ-ÿ\-\'\’\.\,]+?$')
    for word in words:
        if(latin_chars_w_accents.match(word)):
            cleaned_words.append(word)
    return cleaned_words

def test():
    all_words = words.words()
    all_words.extend(stopwords.words())
    all_words.extend(cmudict.words())
    all_words = clean_words(all_words)
    
    all_words = set(all_words)
    
    all_words = list(all_words)
    
    for word in all_words[2000:2100]:
        fs_word = graphemize(word)
        print(f'{word} -> {fs_word}')
        
    """ tested_words = utils.load_data('tested_words.json')
    tested_words = set(tested_words)
    for word in all_words[2000:3000]:
        #fs_word = graphemize(word)
        if(word not in tested_words):
            tested_words.add(word)
            phonemes = phonemize(word, backend='espeak', separator=separator, language='en-us')
            phonemes = phonemes.strip().split(' ')
            bad = [phoneme for phoneme in phonemes if phoneme in bad_chars ]
            
            if(len(bad) > 0):
                print(f'word: {word} -> {phonemes} -> {bad}')
                
            phonemes = set(phonemes)
            letters = letters.union(phonemes)
    letters = list(letters)
    print(len(letters))
    utils.save_data(letters,'ipa_list.json')
    utils.save_data(list(tested_words), 'tested_words.json') """
        #print(f'{word} -> {fs_word}')
            
    #print(all_ipa)
    
def identify_hyphenated_words(tokens: list[Token]):
    hyphenated_words: list[tuple[list[Token], int, int]] = []
    
    non_hyphenated_count = 0
    token_group = []
    start_index = 0
    end_index = 0
    
    for i, token in enumerate(tokens):
        #'Joseph, an able-bodied young man, is running to Wal-Mart to buy some groceries.'
        if(token.text == '-'):
            if(non_hyphenated_count > 1 and len(token_group) == 0):
                start_index = i - 1
            non_hyphenated_count = 0
            if(i > 0):
                token_group.append(tokens[i-1])
                
            token_group.append(token)
        else:
            non_hyphenated_count += 1
            if(non_hyphenated_count > 1 and len(token_group) > 0):
                
                if(i > 0):
                    token_group.append(tokens[i-1])
                end_index = i - 1
                hyphenated_words.append((token_group, start_index, end_index))
                token_group = []
            
    for grouping in hyphenated_words:
        token_info = TokenInfo()
        if(check_property_value('pos', grouping[0])):
            token_info.pos = grouping[0][0].pos_
            token_info.text = ''.join([token.text for token in grouping[0]])
            token_info.wn_ids = [synset.name() for synset in wordnet.synsets(token_info.text, pos=SPACY_POS_TO_WORDNET_POS[token_info.pos])]
    
    return hyphenated_words

def check_property_value(property, obj_list):
    if not obj_list:
        return True  # Return True if list is empty

    first_val = getattr(obj_list[0], property, None)
    for obj in obj_list:
        if getattr(obj, property, None) != first_val:
            return False
    
    return True

def translate(text: str) -> str:
    nlp = spacy.load("en_core_web_trf")
    doc: Doc = nlp(text)
    entity_words = []
    
    tokens = list(doc)
    hyphenated = identify_hyphenated_words(tokens)
    
        
def token_is_word(token: Token) -> bool:
    is_word = True
    if(token.is_punct or token.is_space or token.is_stop):
        is_word = False
    return is_word

def print_token_values(token: Token):
    token_prop_values = {
            "text": token.text,
            "pos": token.pos_,
            'cluster': token.cluster,
            'dep': token.dep_,
            'ent_type': token.ent_type_,
            'ent_iob': token.ent_iob_,
            'ancestors': [ancestor.text for ancestor in token.ancestors],
            'children': [child.text for child in token.children],
            'lefts': [left.text for left in token.lefts],
            'rights': [right.text for right in token.rights],
            'is_alpha': token.is_alpha,
            'head': token.head.text,
            'is_punct': token.is_punct,
            'is_space': token.is_space,
            'is_stop': token.is_stop,
        }
    utils.pretty_print(token_prop_values)
    
def get_word_meanings(word: str):
    
    synsets = wordnet.synsets(word)
    
    meanings = []
    
    for synset in synsets:
        meanings.append(LexLink(synset))
        
    return meanings