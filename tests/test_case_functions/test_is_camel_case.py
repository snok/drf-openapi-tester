import pytest

from django_swagger_tester.case_testers import is_camel_case
from django_swagger_tester.exceptions import CaseError

camel_case_test_data = [
    {'incorrect': 'snake_case', 'correct': 'snakeCase'},
    {'incorrect': 'PascalCase', 'correct': 'pascalCase'},
    {'incorrect': 'kebab-case', 'correct': 'kebabCase'},
    {'incorrect': 'l ower', 'correct': 'lower'},
    {'incorrect': 'UPPER', 'correct': 'uPPER'},
]


def test_camel_cased_words():
    """
    Verifies that our camel case verification function actually works as expected.
    """
    for item in camel_case_test_data:
        is_camel_case(item['correct'], 'test')
        with pytest.raises(CaseError):
            is_camel_case(item['incorrect'], 'test')


def test_less_than_two_chars():
    """
    When the length of an input is less than 2, our regex logic breaks down,
    :return:
    """
    is_camel_case('', 'test')
    with pytest.raises(CaseError):
        is_camel_case(' ', 'test')
        is_camel_case('-', 'test')
        is_camel_case('_', 'test')
        is_camel_case(None, 'test')
        is_camel_case('%', 'test')
        is_camel_case('R', 'test')
    is_camel_case('s', 'test')
