import json
from pathlib import Path

import yaml


class MockRoute:
    def __init__(self, x):
        self.x = x
        self.counter = 0
        self.parameters = [2, 2]

    def get_path(self):
        self.counter += 1
        if self.counter == 2:
            raise IndexError
        return self.x


CURRENT_PATH = Path(__file__).resolve(strict=True).parent


def load_schema(path, load_yaml: bool = True):
    with open(str(CURRENT_PATH) + f'schemas/{path}') as f:
        content = f.read()
        if load_yaml:
            return yaml.load(content, Loader=yaml.FullLoader)
        else:
            return json.loads(content)
