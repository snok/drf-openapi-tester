import pytest

from openapi_tester.exceptions import SpecificationError

test_data = [
    {'input': 'snake_case', 'expected': 'snake_case'},
    {'input': 'PascalCase', 'expected': 'pascal_case'},
    {'input': 'camelCase', 'expected': 'camel_case'},
    {'input': '', 'expected': ''},
    {'input': 'lower', 'expected': 'lower'},
    {'input': 'UPPER', 'expected': 'u_p_p_e_r'},
]


def test_is_camel_case():
    for item in test_data:
        if item['input'] != item['expected']:
            with pytest.raises(SpecificationError):
                is_snake_case(item['input'])
        else:
            is_snake_case(item['input'])
