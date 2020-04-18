import pytest
from django.core.exceptions import ImproperlyConfigured

from django_swagger_tester.drf_yasg.base import validate_response
from django_swagger_tester.exceptions import SwaggerDocumentationError

good_test_data = [
    {
        'url': '/api/v1/cars/correct/',
        'expected_response': [
            {'name': 'Saab', 'color': 'Yellow', 'height': 'Medium height', 'width': 'Very wide', 'length': '2 meters'},
            {'name': 'Volvo', 'color': 'Red', 'height': 'Medium height', 'width': 'Not wide', 'length': '2 meters'},
            {'name': 'Tesla', 'color': 'black', 'height': 'Medium height', 'width': 'Wide', 'length': '2 meters'},
        ],
    },
    {
        'url': '/api/v1/trucks/correct/',
        'expected_response': [
            {'name': 'Saab', 'color': 'Yellow', 'height': 'Medium height', 'width': 'Very wide', 'length': '2 meters'},
            {'name': 'Volvo', 'color': 'Red', 'height': 'Medium height', 'width': 'Not wide', 'length': '2 meters'},
            {'name': 'Tesla', 'color': 'black', 'height': 'Medium height', 'width': 'Wide', 'length': '2 meters'},
        ],
    },
]
bad_test_data = [
    {
        'url': '/api/v1/cars/incorrect/',
        'expected_response': [
            {'name': 'Saab', 'color': 'Yellow', 'height': 'Medium height'},
            {'name': 'Volvo', 'color': 'Red', 'width': 'Not very wide', 'length': '2 meters'},
            {'name': 'Tesla', 'height': 'Medium height', 'width': 'Medium width', 'length': '2 meters'},
        ],
    },
    {
        'url': '/api/v1/trucks/incorrect/',
        'expected_response': [
            {'name': 'Saab', 'color': 'Yellow', 'height': 'Medium height'},
            {'name': 'Volvo', 'color': 'Red', 'width': 'Not very wide', 'length': '2 meters'},
            {'name': 'Tesla', 'height': 'Medium height', 'width': 'Medium width', 'length': '2 meters'},
        ],
    },
]


def test_endpoints_dynamic_schema(client) -> None:  # noqa: TYP001
    """
    Asserts that the validate_response function validates correct schemas successfully.
    """
    for item in good_test_data:
        response = client.get(item['url'])
        assert response.status_code == 200
        assert response.json() == item['expected_response']

        # Test Swagger documentation
        validate_response(response=response, method='GET', route=item['url'])  # type: ignore


def test_bad_endpoints_dynamic_schema(client) -> None:  # noqa: TYP001
    """
    Asserts that the validate_response function validates incorrect schemas successfully.
    """
    for item in bad_test_data:
        response = client.get(item['url'])
        assert response.status_code == 200
        assert response.json() == item['expected_response']

        # Test Swagger documentation
        with pytest.raises(SwaggerDocumentationError, match='The following properties seem to be missing from your response body:'):
            validate_response(response, 'GET', item['url'])  # type: ignore


def test_missing_method_match(client, monkeypatch) -> None:  # noqa: TYP001
    """
    When we fail to index the schema by method, we need to raise an exception.
    """

    def mocked_validate_method(*args, **kwargs):
        pass

    monkeypatch.setattr('django_swagger_tester.drf_yasg.load_schema.validate_inputs', mocked_validate_method)
    for item in bad_test_data:
        response = client.get(item['url'])
        assert response.status_code == 200
        assert response.json() == item['expected_response']

        # Test Swagger documentation
        with pytest.raises(SwaggerDocumentationError, match='Failed indexing schema.'):
            validate_response(response=response, method='gets', route=item['url'])  # type: ignore


def test_missing_status_code_match(client, monkeypatch) -> None:  # noqa: TYP001
    """
    When we fail to index the schema by status code, we need to raise an exception.
    """

    def mocked_unpack_response(*args, **kwargs):
        return {}, 'bad status code'

    monkeypatch.setattr('django_swagger_tester.drf_yasg.base.unpack_response', mocked_unpack_response)
    for item in bad_test_data:
        response = client.get(item['url'])
        with pytest.raises(ImproperlyConfigured, match='`status_code` should be an integer'):
            validate_response(response=response, method='GET', route=item['url'])  # type: ignore
