from openapi_tester.utils import camel_case


def test_camel_case():
    test_data = [
        {'input': 'snake_case', 'expected': 'snakeCase'},
        {'input': 'PascalCase', 'expected': 'pascalCase'},
        {'input': 'camelCase', 'expected': 'camelCase'},
        {'input': '', 'expected': ''},
        {'input': 'lower', 'expected': 'lower'},
        {'input': 'UPPER', 'expected': 'uPPER'},
    ]
    for item in test_data:
        assert camel_case(item['input']) == item['expected']
