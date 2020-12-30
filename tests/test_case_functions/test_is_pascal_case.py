import pytest

from django_openapi_response_tester.case_testers import is_pascal_case
from django_openapi_response_tester.exceptions import CaseError

pascal_case_test_data = [
    {'incorrect': 'snake_case', 'correct': 'SnakeCase'},
    {'incorrect': 'camelCase', 'correct': 'CamelCase'},
    {'incorrect': 'kebab-case', 'correct': 'KebabCase'},
    {'incorrect': 'l ower', 'correct': 'Lower'},
    {'incorrect': 'uPPER', 'correct': 'UPPER'},
]


def test_pascal_cased_words():
    """
    Verifies that our pascal case verification function actually works as expected.
    """
    for item in pascal_case_test_data:
        is_pascal_case(item['correct'], 'test')
        with pytest.raises(CaseError):
            is_pascal_case(item['incorrect'], 'test')


def test_less_than_two_chars():
    """
    When the length of an input is less than 2, our regex logic breaks down,
    :return:
    """
    is_pascal_case('', 'test')
    with pytest.raises(CaseError):
        is_pascal_case(' ', 'test')
        is_pascal_case('-', 'test')
        is_pascal_case('_', 'test')
        is_pascal_case(None, 'test')
        is_pascal_case('%', 'test')
        is_pascal_case('s', 'test')
    is_pascal_case('S', 'test')
