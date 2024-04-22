from bs4 import BeautifulSoup
from bs4.element import Tag
import json

ORTHO_CATEGORIES_HTML = './html/ortho_categories.html'
ORTHO_CATEGORIES_JSON = './data/ortho_categories.json'
PHONETIC_INV_HTML = './html/phonetic_inventory.html'
PHONETIC_INV_JSON = './data/phonetic_inventory.json'

def get_file(file_path: str) -> str:
    with open(file_path, 'r') as file:
        if(file_path.endswith('.json')):
            return json.load(file)
        return file.read()

def write_file(file_path: str, data: str | dict) -> None:
    with open(file_path, 'w') as file:
        if(isinstance(data, dict)):
            data = json.dumps(data, indent=4)
        
        file.write(data)
        
def get_phonetic_inventory():
    html_string = get_file(PHONETIC_INV_HTML)

    # Use BeautifulSoup to parse it into a searchable object
    document = BeautifulSoup(html_string, 'html.parser')

    body = document.find('body')

    phonetic_inventory = {}

    for i in range(46):
        element_id = f'list_{i}'
        element = body.find('div', {'id': element_id})

        if element:
            spans = element.find_all('span')
            ipa = spans[2].text.strip()
            grapheme = spans[3].text.strip().replace('<','').replace('>','')
            phonetic_inventory[grapheme] = ipa

    write_file(PHONETIC_INV_JSON, phonetic_inventory)
    
def get_orth_categories():
    html_string = get_file(ORTHO_CATEGORIES_HTML)

    # Use BeautifulSoup to parse it into a searchable object
    document = BeautifulSoup(html_string, 'html.parser')

    inputs = document.find_all('input')
    
    ortho_categories = {}
    
    for item in inputs:
        if(isinstance(item, Tag )):
            value = item.attrs.get('value')
            if(isinstance(value, str)):
                if(len(value) == 1 and value.upper() == value):
                    category = value
                else:
                    category_range = value.split(',')
                    
                    category_range = list(filter(lambda x: x != '', category_range))
                    if(ortho_categories.get(category) is None):
                        ortho_categories[category] = category_range
    
    write_file(ORTHO_CATEGORIES_JSON, ortho_categories)