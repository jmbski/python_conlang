import json, sys
class DictClass(dict):
    
    def __init_subclass__(cls) -> None:
        return super().__init_subclass__()
    
    def __init__(self, *args, **kwargs) -> None:
        return super().__init__(*args, **kwargs)
    
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)
    
    def __getitem__(self, key):
        
        return super().__getitem__(key)
    
    def __setitem__(self, key, value):
        super().__setattr__(key, value)
        return super().__setitem__(key, value)
    
    def __getattribute__(self, name: str):
        
        return super().__getattribute__(name)
    
    def __setattr__(self, name: str, value) -> None:
        self.__setitem__(name, value)

DATA_PATH = '/home/joseph/coding_base/silverlight/conlang/python/data/'
LIST_STR_PATTERN = r'^\[(.*)\]$'
LIST_STR_SEPARATOR_PATTERN = r'(\w[^,]*\w)'
SINGLE_QUOTE_PATTERN = r"^'(.*)'$"
DOUBLE_QUOTE_PATTERN = r'^"(.*)"$'
NLTK_DOWNLOADS = {
    'swadesh': '/home/joseph/nltk_data/corpora/swadesh.zip',
    'wordnet': '/home/joseph/nltk_data/corpora/wordnet.zip',
    'omw-1.4': '/home/joseph/nltk_data/corpora/omw-1.4.zip',
    'wordnet_ic': '/home/joseph/nltk_data/corpora/wordnet_ic.zip',
    'stopwords': '/home/joseph/nltk_data/corpora/stopwords.zip',
    'words': '/home/joseph/nltk_data/corpora/words.zip',
    'cmudict': '/home/joseph/nltk_data/corpora/cmudict.zip',
}
NLTK_DATA_DIR = '/home/joseph/nltk_data'

GLOBAL_VARS = DictClass()
GLOBAL_VARS.is_gunicorn = 'gunicorn' in sys.argv[0].lower()
LOG_CONTEXTS: dict = {}
ORTHO_CATEGORIES = {
    "A": [ "a" ],
    "B": [ "à", "ê", "é", "ô", "ò", "ö", "û", "ü" ],
    "C": [ "c", "ç", "kh" ],
    "D": [ "d", "t", "th", "`th" ],
    "E": [ "ê", "e", "é" ],
    "F": [ "f" ],
    "G": [ "g", "j" ],
    "H": [ "'h", "h" ],
    "I": [ "i" ],
    "J": [ "a", "e", "i", "o", "u" ],
    "K": [ "'h", "'sh", "b", "bv", "c", "ç", "d", "f", "g", "h", "j", "kh", "l", "m", "n", "p", "pf", "r", "s", "sh", "t", "tch", "th", "v", "w", "y", "ž", "z", "zh", "zsh", "`th" ],
    "L": [ "l" ],
    "M": [ "m", "n" ],
    "O": [ "ô", "ò", "o", "ö" ],
    "P": [ "p", "pf", "b", "bv" ],
    "R": [ "r" ],
    "S": [ "'sh", "sh", "tch", "s" ],
    "U": [ "û", "ü", "u" ],
    "V": [ "a", "à", "ê", "e", "é", "i", "ô", "ò", "o", "ö", "û", "ü", "u" ],
    "W": [ "v", "w" ],
    "Y": [ "y" ],
    "Z": [ "ž", "z", "zh", "zsh" ]
}

IPA_ESCAPE = {
    '1': 'i',
    'ᵻ': 'ɨ', 
    'ɚ': 'ɹ'
}

LOG_CONFIG = json.load(open('/home/joseph/coding_base/configs/log_config.json', 'r'))

SYLLABLES: dict = {
    'AMI': 1000,
    'ADI': 1000,
    'AME': 900,
    'ADE': 950,
    'CLV': 900,
    'AE': 800,
    'AI': 950,
    'EIL': 900,
    'AL': 750,
    
    'ZAI': 600,
    'ZOR': 650,
    'JZE': 650,
    'JZA': 550,
    'UL': 650,
    'UR': 500,
    'HJ': 450,

    'JAI': 425,
    'LAI': 425,
    'LEI': 420,
    'AEL': 500,
    'JLS': 400,

    'KJM': 375,
    'KJD': 350,
    'DJC': 345,
    'DJM': 340,
    'SUL': 385,
    'CUL': 400,

    'HJC': 300,
    'MJMO': 325,
    'CDJ': 275,
    'WJL': 265,
    'WJS': 250,
    'YCJ': 245,

    'HBL': 235,
    'CBP': 230,
    'WBP': 225,
    'DBJ': 225,
    'CBZ': 220,
    'MJY': 215,
}
# pairs of orthography group labels and their weight of occurance

PHONETIC_INVENTORY = {
    "r": "ɹ",
    "s": "s",
    "z": "z",
    "ž": "ts",
    "l": "l",
    "n": "n",
    "t": "t",
    "d": "d",
    "f": "ɸ",
    "m": "m",
    "p": "p",
    "b": "b",
    "th": "θ",
    "`th": "ð",
    "h": "h",
    "'h": "ɦ",
    "y": "j",
    "ie": "ʝ",
    "ç": "c",
    "v": "v",
    "pf": "pf",
    "bv": "bv",
    "sh": "ʃ",
    "zh": "ʒ",
    "j": "dʒ",
    "'sh": "ʂ",
    "zsh": "ʐ",
    "kh": "kx",
    "c": "k",
    "g": "ɢ",
    "w": "w",
    "tch": "tɕ",
    "u": "u",
    "ö": "ʉ",
    "û": "ɨ",
    "ü": "y",
    "i": "i",
    "ê": "ɜ",
    "ô": "œ",
    "e": "ɛ",
    "o": "o",
    "é": "e",
    "ò": "ə",
    "a": "a",
    "à": "æ"
}

GRAPHEME_LOOKUP = {
    "ɹ": "r",
    "s": "s",
    "z": "z",
    "ts": "ž",
    "l": "l",
    "n": "n",
    "t": "t",
    "d": "d",
    "ɸ": "f",
    "m": "m",
    "p": "p",
    "b": "b",
    "θ": "th",
    "ð": "`th",
    "h": "h",
    "ɦ": "'h",
    "j": "y",
    "ʝ": "ie",
    "c": "ç",
    "v": "v",
    "pf": "pf",
    "bv": "bv",
    "ʃ": "sh",
    "ʒ": "zh",
    "dʒ": "j",
    "dʒ": "j",
    "ʂ": "'sh",
    "ʐ": "zsh",
    "kx": "kh",
    "k": "c",
    "ɢ": "g",
    "w": "w",
    "tɕ": "tch",
    "u": "u",
    "ʉ": "ö",
    "ɨ": "û",
    "y": "ü",
    "i": "i",
    "ɜ": "ê",
    "œ": "ô",
    "ɛ": "e",
    "o": "o",
    "e": "é",
    "ə": "ò",
    "a": "a",
    "æ": "à"
}

POS = {
    'n': 'Noun',
    'v': 'Verb',
    'a': 'Adjective',
    'r': 'Adverb',
    's': 'Satellite Adjective',
    'Noun': 'n',
    'Verb': 'v',
    'Adjective': 'a',
    'Adverb': 'r',
    'Satellite Adjective': 's',
    'noun': 'n',
    'verb': 'v',
    'adjective': 'a',
    'adverb': 'r',
    'satellite adjective': 's'
}

LEIPZIG_JAKARTA = ['fire','nose','to','water','mouth','tongue','blood','bone','2nd','root','to','breast','rain','1st','name','louse','wing','flesh','arm','fly','night','ear','neck','far','to','house','stone','bitter','to','tooth','hair','big','one','who','3rd','to','leg','horn','this','fish','yesterday','to','black','navel','to','to','back','wind','smoke','what','child','egg','to','new','to','not','good','to','knee','sand','to','to','soil','leaf','red','liver','to','skin','to','to','ant','heavy','to','old','to','thigh','thick','long','to','wood','to','to','eye','ash','tail','dog','to','to','to','sweet','rope','shade','bird','salt','small','wide','star','in','hard','to']