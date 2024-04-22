from __future__ import annotations
import json, re
from random import random, choices
import os, time

from modules import (
    word_reader,
    decorators
)

from modules.common import (
    PHONETIC_INVENTORY,
    GRAPHEME_LOOKUP,
    SYLLABLES,
    ORTHO_CATEGORIES
)

def get_ortho_categories():
    path = './data/ortho_categories.json'
    with open(path, 'r') as file:
        return json.load(file)
    
def get_phonetic_inventory():
    path = './data/phonetic_inventory.json'
    with open(path, 'r') as file:
        return json.load(file)



def grapheme_to_IPA(grapheme_str, grapheme_dictionary=None):
    if(not grapheme_dictionary):
        grapheme_dictionary = PHONETIC_INVENTORY
    sorted_graphemes = sorted(grapheme_dictionary.keys(), key=len, reverse=True)
    regex_pattern = "|".join(re.escape(key) for key in sorted_graphemes)
    return re.sub(regex_pattern, lambda match: grapheme_dictionary[match.group(0)], grapheme_str)
    
def speak_IPA(text):
    os.system(f'espeak -v en "{text}" --ipa=3')
    
def speak_words():
    with open('./data/word_bank.json', 'r') as reader:
        words = json.load(reader)
        browser = None
        for word in words.values():
            if(not browser):
                browser = word_reader.automate_ipa_reader(word)
            else:
                word_reader.automate_ipa_reader(word, browser=browser)
            pause = input()
            if(pause == 'q'):
                exit()
             
def generate_syllable(category: str):
    syllable = []
    
    for letter in category:
        phonemes = ORTHO_CATEGORIES.get(letter)
        #print(phonemes)
        if(phonemes):
            index = int(random() * len(phonemes))
            #print(len(phonemes), index, phonemes[index])
            phoneme = phonemes[index]
            ipa = PHONETIC_INVENTORY.get(phoneme)
            if(not ipa):
                print(phoneme, 'not found')
            else:
                syllable.append(phoneme)
    
    
    
    return syllable

def get_category_group():
    keys = list(SYLLABLES.keys())
    weights = list(SYLLABLES.values())
    return choices(keys, weights)[0]

def to_graphemes(chars: list[str]):
    grapheme_word = ''
    
    for char in chars:
        if(not GRAPHEME_LOOKUP.get(char)):
            print(char, grapheme_word, chars, 'not found')
            continue
        grapheme_word += GRAPHEME_LOOKUP.get(char)
        
    return grapheme_word

def to_ipa(chars: list[str]):
    ipa_word = ''
    for char in chars:
        ipa_word += PHONETIC_INVENTORY.get(char)
    return ipa_word
    
def generate_word(syllables: int = None, minimum: int = 1, maximum: int = 3):
    if(syllables):
        count = syllables
    else:
        count = int(random() * (maximum - minimum + 1)) + minimum
    

    word_chars = []
    
    
    for _ in range(count):
        category = get_category_group()
        word_chars.extend(generate_syllable(category))
    
    #print(word_chars)
    word = ''.join(word_chars)
    word_ipa = to_ipa(word_chars)
        
        
    return word, word_ipa

def generate_words():
    for _ in range(100):
        print(generate_word())
        
def sort_dict_by_key(obj: dict):
    return dict(sorted(obj.items(), key=lambda item: item[0]))
        
def add_to_word_bank():
    with open('./data/word_bank.json', 'r') as reader:
        words = json.load(reader)
        for _ in range(1000):
            word, word_ipa = generate_word()
            if(word not in words):
                words[word] = word_ipa
        words = sort_dict_by_key(words)    
        with open('./data/word_bank.json', 'w') as writer:
            writer.write(json.dumps(words, indent=4,ensure_ascii=False))

def test():
    for category, letters in ORTHO_CATEGORIES.items():
        for letter in letters:
            phoneme = PHONETIC_INVENTORY.get(letter)
            if(not phoneme):
                print(letter)
                
decorators.log_module_functs(globals())