import pytest

from django_swagger_tester.case_testers import is_snake_case
from django_swagger_tester.exceptions import CaseError

snake_case_test_data = [
    {'incorrect': 'camelCase', 'correct': 'camel_case'},
    {'incorrect': 'PascalCase', 'correct': 'pascal_case'},
    {'incorrect': 'kebab-case', 'correct': 'kebab_case'},
    {'incorrect': 'l ower', 'correct': 'lower'},
    {'incorrect': 'UPPER', 'correct': 'u_p_p_e_r'},
]


def test_snake_cased_words():
    """
    Verifies that our snake case verification function actually works as expected.
    """
    for item in snake_case_test_data:
        is_snake_case(item['correct'])
        with pytest.raises(CaseError):
            is_snake_case(item['incorrect'])


def test_less_than_two_chars():
    """
    When the length of an input is less than 2, our regex logic breaks down,
    :return:
    """
    is_snake_case('')
    with pytest.raises(CaseError):
        is_snake_case(' ')
        is_snake_case('-')
        is_snake_case('_')
        is_snake_case(None)
        is_snake_case('%')
        is_snake_case('R')
    is_snake_case('s')
