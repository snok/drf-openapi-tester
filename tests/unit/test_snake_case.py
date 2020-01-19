from openapi_tester.utils import snake_case


def test_snake_case():
    test_data = [
        {'input': 'snake_case', 'expected': 'snake_case'},
        {'input': 'PascalCase', 'expected': 'pascal_case'},
        {'input': 'camelCase', 'expected': 'camel_case'},
        {'input': '', 'expected': ''},
        {'input': 'lower', 'expected': 'lower'},
        {'input': 'UPPER', 'expected': 'upper'},
    ]
    for item in test_data:
        assert snake_case(item['input']) == item['expected']
