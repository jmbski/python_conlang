from modules import (
    utils,
)
import json

def get_json_page(data: dict | list, indent: int = 4) -> str:
    html = utils.load_data('json_page.html')
    html = '\n'.join(html)
    json_data = json.dumps(data, indent=4)
    html = html.replace('py_json_data', json_data)
    return html