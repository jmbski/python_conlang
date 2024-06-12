""" Base ideas:

Start with leipzig-jarkarta and swadish combined word list
Then, use nltk/wordnet to retrieve definitions
Create a list of words with definitions
This will get parsed into the sqlite DB
words -> eng_words table, definitions -> definitions table
These relations will also be added to a join table

..

Alternatively, I could just create a service that retrieves the synset
for a given word and returns the whole thing as a JSON object
"""
from warskald import GLOBALS, utils, AttrDict
from nltk.corpus.reader.wordnet import Synset, Lemma
from nltk.corpus import swadesh, wordnet
import nltk

GLOBALS.DATA_PATH = '/home/joseph/coding_base/silverlight/conlang/python/data/'

LJ_WORDS = utils.load_data('leipzig-jakarta.json')
SWADESH_WORDS = utils.load_data('swadesh_en.json')
COMBINED = list(set(LJ_WORDS + SWADESH_WORDS))


def get_synset_json(synset: str | Synset) -> dict:
    """ Returns a JSON object that contains the synset of a given word """
    if(isinstance(synset, str)):
        synset = wordnet.synset(synset)
        
    if(isinstance(synset, Synset)):
        synset_json = {
            'eng_word': synset_name(synset),
            'synset_id': synset.name(),
            'pos': synset.pos(),
            'definition': synset.definition(),
            'examples': synset.examples(),
            'lemmas': [lemma.name() for lemma in synset.lemmas()],
            'hypernyms': [hypernym.name() for hypernym in synset.hypernyms()],
            'hyponyms': [hyponym.name() for hyponym in synset.hyponyms()],
            'holonyms': [holonym.name() for holonym in synset.member_holonyms()],
            'meronyms': [meronym.name() for meronym in synset.part_meronyms()],
        }
        
        return AttrDict(synset_json)
    return {}



def get_synsets_json(word: str, nest=True) -> list:
    """ Returns a JSON object that contains the synset(s) of a given word """
    if('.' in word):
        return [get_synset_json(word)]
    
    synsets = wordnet.synsets(word)
    if not synsets:
        return []
    
    return [ get_synset_json(synset) for synset in synsets ]
    
def get_definition(synset_id: str) -> dict:
    """ Returns the definition of a given synset """
    synset = wordnet.synset(synset_id)
    if(synset):
        return { 'word': synset.name(), 'definition': synset.definition() }


def synset_name(wn_object: Synset | Lemma) -> str:
    return wn_object.name().split('.')[0] if isinstance(wn_object, Synset) else wn_object.name()

def main():
    args = utils.get_inputs()
    word = args.word or args.w
    if(isinstance(word, str)):
        synset_json = get_synset_json(word)
    else:
        synset_json = {}
    
    if(isinstance(synset_json, (dict, list))):
        utils.pretty_print(synset_json)
        
if(__name__ == '__main__'):
    utils.pretty_print(get_synset_json("fire.n.04"))