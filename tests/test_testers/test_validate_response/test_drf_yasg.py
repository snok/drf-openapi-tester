from django.core.exceptions import ImproperlyConfigured

import pytest

from response_tester.exceptions import SwaggerDocumentationError
from response_tester.testing import validate_response

good_test_data = [
    {
        'url': '/api/v1/cars/correct',
        'expected_response': [
            {'name': 'Saab', 'color': 'Yellow', 'height': 'Medium height', 'width': 'Very wide', 'length': '2 meters'},
            {'name': 'Volvo', 'color': 'Red', 'height': 'Medium height', 'width': 'Not wide', 'length': '2 meters'},
            {'name': 'Tesla', 'color': 'black', 'height': 'Medium height', 'width': 'Wide', 'length': '2 meters'},
        ],
    },
    {
        'url': '/api/v1/trucks/correct',
        'expected_response': [
            {'name': 'Saab', 'color': 'Yellow', 'height': 'Medium height', 'width': 'Very wide', 'length': '2 meters'},
            {'name': 'Volvo', 'color': 'Red', 'height': 'Medium height', 'width': 'Not wide', 'length': '2 meters'},
            {'name': 'Tesla', 'color': 'black', 'height': 'Medium height', 'width': 'Wide', 'length': '2 meters'},
        ],
    },
]
bad_test_data = [
    {
        'url': '/api/v1/cars/incorrect',
        'expected_response': [
            {'name': 'Saab', 'color': 'Yellow', 'height': 'Medium height'},
            {'name': 'Volvo', 'color': 'Red', 'width': 'Not very wide', 'length': '2 meters'},
            {'name': 'Tesla', 'height': 'Medium height', 'width': 'Medium width', 'length': '2 meters'},
        ],
    },
    {
        'url': '/api/v1/trucks/incorrect',
        'expected_response': [
            {'name': 'Saab', 'color': 'Yellow', 'height': 'Medium height'},
            {'name': 'Volvo', 'color': 'Red', 'width': 'Not very wide', 'length': '2 meters'},
            {'name': 'Tesla', 'height': 'Medium height', 'width': 'Medium width', 'length': '2 meters'},
        ],
    },
    {
        'url': '/api/v1/trucks/incorrect',
        'expected_response': [
            {'name': 'Saab', 'color': 'Yellow', 'height': 'Medium height'},
            {'name': 'Volvo', 'color': 'Red', 'width': 'Not very wide', 'length': '2 meters'},
            {'name': 'Tesla', 'height': 'Medium height', 'width': 'Medium width', 'length': '2 meters'},
        ],
    },
]


def test_endpoints_dynamic_schema(client, transactional_db) -> None:  # noqa: TYP001
    """
    Asserts that the validate_response function validates correct schemas successfully.
    """
    for item in good_test_data:
        response = client.get(item['url'])
        assert response.status_code == 200
        assert response.json() == item['expected_response']

        # Test Swagger documentation
        validate_response(response=response, method='GET', route=item['url'])  # type: ignore


def test_bad_endpoints_dynamic_schema(client, transactional_db) -> None:  # noqa: TYP001
    """
    Asserts that the validate_response function validates incorrect schemas successfully.
    """
    for item in bad_test_data:
        response = client.get(item['url'])
        assert response.status_code == 200
        assert response.json() == item['expected_response']

        # Test Swagger documentation
        with pytest.raises(
            SwaggerDocumentationError, match='The following properties seem to be missing from your response body:'
        ):
            validate_response(response, 'GET', item['url'], verbose=True)  # type: ignore


def test_bad_method(client, monkeypatch, transactional_db) -> None:  # noqa: TYP001
    """
    When we fail to index the schema by method, we need to raise an exception.
    """
    for item in bad_test_data:
        response = client.get(item['url'])
        assert response.status_code == 200
        assert response.json() == item['expected_response']

        # Test Swagger documentation
        with pytest.raises(
            ImproperlyConfigured,
            match='Method `gets` is invalid. Should be one of: GET, POST, PUT, PATCH, DELETE, OPTIONS, HEAD.',
        ):
            validate_response(response=response, method='gets', route=item['url'])  # type: ignore


def test_missing_status_code_match(client, monkeypatch, transactional_db) -> None:  # noqa: TYP001
    """
    When we fail to index the schema by status code, we need to raise an exception.
    """

    def mocked_unpack_response(*args, **kwargs):
        return {}, 'bad status code'

    monkeypatch.setattr('response_tester.testing.unpack_response', mocked_unpack_response)
    for item in bad_test_data:
        response = client.get(item['url'])
        with pytest.raises(ImproperlyConfigured, match='`status_code` should be an integer'):
            validate_response(response=response, method='GET', route=item['url'])  # type: ignore
