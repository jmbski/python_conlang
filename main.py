import os, json
from modules import (
    common,
    utils
)
from modules.lang_data import LanguageData
from nltk.corpus import swadesh, wordnet
from PyDictionary import PyDictionary

somevalue = 5
def get_lang(lang_name: str) -> LanguageData:
    settings_path = os.path.abspath('./data/language_configs.json')
    
    if(os.path.exists(settings_path)):
        with open(settings_path, 'r') as json_data:
            settings = json.load(json_data)
            lang_config = settings.get(lang_name, {})
            if(lang_config):
                return LanguageData(lang_config)

def main():
    base_words = swadesh.words('en')
    for word in common.LEIPZIG_JAKARTA:
        if(word not in base_words):
            base_words.append(word)
            
    base_words.sort()
    py_dict = PyDictionary()
    for word in base_words[0:10]:
        print(f"{word}: {py_dict.meaning(word)}")

if __name__ == "__main__":
    main()