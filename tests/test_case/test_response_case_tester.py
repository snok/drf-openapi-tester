import pytest

from django_swagger_tester.case.base import ResponseCaseTester
from django_swagger_tester.exceptions import CaseError

valid_cc_response = [
    {
        'camelCasedKey': 'NotCamelCasedValue',
        'camelCasedSecondKey': {'camelCasedThirdKey': ['oNe', 'Two', 'THREE', [{'nestedListWithDict': 2}]]},
    }
]
valid_sc_response = [
    {
        'snake_cased_key': 'NotSnakeCasedValue',
        'snake_cased_second_key': {'snake_cased_third_key': ['oNe', 'Two', 'THREE', [{'nested_list_with_dict': 2}]]},
    }
]


def test_valid_camel_case_response(monkeypatch):
    class MockSettings:
        CASE = 'camelCase'

    monkeypatch.setattr('django_swagger_tester.case.base.settings', MockSettings)
    ResponseCaseTester(response_data=valid_cc_response)
    ResponseCaseTester(response_data=valid_cc_response[0])


def test_invalid_camel_case_response(monkeypatch):
    class MockSettings:
        CASE = 'camelCase'

    monkeypatch.setattr('django_swagger_tester.case.base.settings', MockSettings)
    with pytest.raises(CaseError, match='The property `snake_cased_key` is not properly camelCased'):
        ResponseCaseTester(response_data=valid_sc_response)
        ResponseCaseTester(response_data=valid_sc_response[0])


def test_valid_snake_case_response(monkeypatch):
    class MockSettings:
        CASE = 'snake_case'

    monkeypatch.setattr('django_swagger_tester.case.base.settings', MockSettings)
    ResponseCaseTester(response_data=valid_sc_response)
    ResponseCaseTester(response_data=valid_sc_response[0])


def test_invalid_snake_case_response(monkeypatch):
    class MockSettings:
        CASE = 'snake_case'

    monkeypatch.setattr('django_swagger_tester.case.base.settings', MockSettings)
    with pytest.raises(CaseError, match='The property `camelCasedKey` is not properly snake_cased'):
        ResponseCaseTester(response_data=valid_cc_response)
        ResponseCaseTester(response_data=valid_cc_response[0])


def test_skipped_case_check(caplog):
    ResponseCaseTester(response_data='test')
    assert 'Skipping case check' in [record.message for record in caplog.records]


def test_bad_type_passed_to_test_dict():
    """
    Make sure we're validating the input type.
    """
    r = ResponseCaseTester(response_data=None)
    with pytest.raises(ValueError, match='Expected dictionary, but received <class \'str\'>'):
        r.test_dict(dictionary='test')


def test_bad_type_passed_to_test_list():
    """
    Make sure we're validating the input type.
    """
    r = ResponseCaseTester(response_data=None)
    with pytest.raises(ValueError, match='Expected list, but received <class \'str\'>'):
        r.test_list(items='test')
