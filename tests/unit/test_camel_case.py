import pytest

from openapi_tester.case import is_camel_case
from openapi_tester.exceptions import SpecificationError
from openapi_tester.utils import camel_case

test_data = [
    {'input': 'snake_case', 'expected': 'snakeCase'},
    {'input': 'PascalCase', 'expected': 'pascalCase'},
    {'input': 'camelCase', 'expected': 'camelCase'},
    {'input': '', 'expected': ''},
    {'input': 'lower', 'expected': 'lower'},
    {'input': 'UPPER', 'expected': 'uPPER'},
]


def test_camel_case():
    for item in test_data:
        assert camel_case(item['input']) == item['expected']


def test_is_camel_case():
    for item in test_data:
        if item['input'] != item['expected']:
            with pytest.raises(SpecificationError):
                is_camel_case(item['input'])
        else:
            is_camel_case(item['input'])
