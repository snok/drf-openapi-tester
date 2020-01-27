import pytest

from openapi_tester.case import case_check, is_camel_case, is_snake_case, skip


def test_case_check_is_valid():
    assert case_check('camel case') == is_camel_case
    assert case_check('snake case') == is_snake_case
    assert case_check(None) == skip


def test_case_check_invalid_inputs():
    for item in ['case', '', 1]:
        with pytest.raises(KeyError):
            case_check(item)
