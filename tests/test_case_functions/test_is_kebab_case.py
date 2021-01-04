import pytest

from openapi_tester.case_testers import is_kebab_case
from openapi_tester.exceptions import CaseError

kebab_case_test_data = [
    {'incorrect': 'snake_case', 'correct': 'snake-case'},
    {'incorrect': 'PascalCase', 'correct': 'pascal-case'},
    {'incorrect': 'camelCase', 'correct': 'camel-case'},
    {'incorrect': 'l ower', 'correct': 'lower'},
    {'incorrect': 'UPPER', 'correct': 'u-p-p-e-r'},
]


def test_kebab_cased_words():
    """
    Verifies that our kebab case verification function actually works as expected.
    """
    for item in kebab_case_test_data:
        is_kebab_case(item['correct'], 'test')
        with pytest.raises(CaseError):
            is_kebab_case(item['incorrect'], 'test')


def test_less_than_two_chars():
    """
    When the length of an input is less than 2, our regex logic breaks down,
    :return:
    """
    is_kebab_case('', 'test')
    with pytest.raises(CaseError):
        is_kebab_case(' ', 'test')
        is_kebab_case('-', 'test')
        is_kebab_case('_', 'test')
        is_kebab_case(None, 'test')
        is_kebab_case('%', 'test')
        is_kebab_case('R', 'test')
    is_kebab_case('s', 'test')
