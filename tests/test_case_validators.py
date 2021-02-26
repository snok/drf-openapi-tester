import pytest

from openapi_tester.case_testers import is_camel_case, is_kebab_case, is_pascal_case, is_snake_case
from openapi_tester.exceptions import CaseError

camel_case_test_data = [
    {"incorrect": "snake_case", "correct": "snakeCase"},
    {"incorrect": "PascalCase", "correct": "pascalCase"},
    {"incorrect": "kebab-case", "correct": "kebabCase"},
    {"incorrect": "UPPER", "correct": "upper"},
]


def test_camel_cased_words():
    """
    Verifies that our camel case verification function actually works as expected.
    """
    for item in camel_case_test_data:
        is_camel_case(item["correct"])
        with pytest.raises(CaseError):
            is_camel_case(item["incorrect"])


def test_camel_case_less_than_two_chars():
    """
    When the length of an input is less than 2, our regex logic breaks down,
    """
    is_camel_case("")
    is_camel_case("s")
    is_camel_case(" ")
    is_camel_case("_")
    is_camel_case("%")
    with pytest.raises(CaseError):
        is_camel_case("-")


kebab_case_test_data = [
    {"incorrect": "snake_case", "correct": "snake-case"},
    {"incorrect": "PascalCase", "correct": "pascal-case"},
    {"incorrect": "camelCase", "correct": "camel-case"},
    {"incorrect": "UPPER", "correct": "u-p-p-e-r"},
]


def test_kebab_cased_words():
    """
    Verifies that our kebab case verification function actually works as expected.
    """
    for item in kebab_case_test_data:
        is_kebab_case(item["correct"])
        with pytest.raises(CaseError):
            is_kebab_case(item["incorrect"])


def test_kebab_case_less_than_two_chars():
    """
    When the length of an input is less than 2, our regex logic breaks down,
    :return:
    """
    is_kebab_case("")
    is_kebab_case("s")
    is_kebab_case("")
    is_kebab_case(" ")
    is_kebab_case("-")
    is_kebab_case("%")
    with pytest.raises(CaseError):
        is_kebab_case("R")


pascal_case_test_data = [
    {"incorrect": "snake_case", "correct": "SnakeCase"},
    {"incorrect": "camelCase", "correct": "CamelCase"},
    {"incorrect": "kebab-case", "correct": "KebabCase"},
    {"incorrect": "l ower", "correct": "Lower"},
    {"incorrect": "uPPER", "correct": "Upper"},
]


def test_pascal_cased_words():
    """
    Verifies that our pascal case verification function actually works as expected.
    """
    for item in pascal_case_test_data:
        is_pascal_case(item["correct"])
        with pytest.raises(CaseError):
            is_pascal_case(item["incorrect"])


def test_pascal_case_less_than_two_chars():
    """
    When the length of an input is less than 2, our regex logic breaks down,
    :return:
    """
    is_pascal_case("")
    is_pascal_case("S")
    is_pascal_case(" ")
    is_pascal_case("_")
    is_pascal_case("%")
    with pytest.raises(CaseError):
        is_pascal_case("-")
    with pytest.raises(CaseError):
        is_pascal_case("s")


snake_case_test_data = [
    {"incorrect": "camelCase", "correct": "camel_case"},
    {"incorrect": "PascalCase", "correct": "pascal_case"},
    {"incorrect": "kebab-case", "correct": "kebab_case"},
    {"incorrect": "UPPER", "correct": "u_p_p_e_r"},
]


def test_snake_cased_words():
    """
    Verifies that our snake case verification function actually works as expected.
    """
    for item in snake_case_test_data:
        is_snake_case(item["correct"])
        with pytest.raises(CaseError):
            is_snake_case(item["incorrect"])


def test_snake_case_less_than_two_chars():
    """
    When the length of an input is less than 2, our regex logic breaks down,
    :return:
    """
    is_snake_case("")
    is_snake_case("s")
    is_snake_case(" ")
    is_snake_case("_")
    is_snake_case("%")
    with pytest.raises(CaseError):
        is_snake_case("-")
    with pytest.raises(CaseError):
        is_snake_case("R")
