import json
from pathlib import Path


def save_data(data):
    path = Path('expenses.json')
    file_data = json.loads(path.read_text(encoding='utf-8'))
    file_data["expenses"].append(data)
    path.write_text(json.dumps(file_data, indent=4, ensure_ascii=False), encoding='utf-8')


def clear_data():
    with open('expenses.json', 'r') as r:
        data = json.load(r)

    data['expenses'] = []

    with open('expenses.json', 'w') as w:
        json.dump(data, w)
