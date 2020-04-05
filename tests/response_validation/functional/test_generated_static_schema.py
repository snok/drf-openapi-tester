import pytest
from django.conf import settings as django_settings

from django_swagger_tester.exceptions import SwaggerDocumentationError
from django_swagger_tester.response_validation.static_schema import validate_response

good_test_data = [
    {
        'url': '/cars/correct/',
        'expected_response': [
            {'name': 'Saab', 'color': 'Yellow', 'height': 'Medium height', 'width': 'Very wide', 'length': '2 meters'},
            {'name': 'Volvo', 'color': 'Red', 'height': 'Medium height', 'width': 'Not wide', 'length': '2 meters'},
            {'name': 'Tesla', 'color': 'black', 'height': 'Medium height', 'width': 'Wide', 'length': '2 meters'},
        ],
    },
    {
        'url': '/trucks/correct/',
        'expected_response': [
            {'name': 'Saab', 'color': 'Yellow', 'height': 'Medium height', 'width': 'Very wide', 'length': '2 meters'},
            {'name': 'Volvo', 'color': 'Red', 'height': 'Medium height', 'width': 'Not wide', 'length': '2 meters'},
            {'name': 'Tesla', 'color': 'black', 'height': 'Medium height', 'width': 'Wide', 'length': '2 meters'},
        ],
    },
]

bad_test_data = [
    {
        'url': '/cars/incorrect/',
        'expected_response': [
            {'name': 'Saab', 'color': 'Yellow', 'height': 'Medium height'},
            {'name': 'Volvo', 'color': 'Red', 'width': 'Not very wide', 'length': '2 meters'},
            {'name': 'Tesla', 'height': 'Medium height', 'width': 'Medium width', 'length': '2 meters'},
        ],
    },
    {
        'url': '/trucks/incorrect/',
        'expected_response': [
            {'name': 'Saab', 'color': 'Yellow', 'height': 'Medium height'},
            {'name': 'Volvo', 'color': 'Red', 'width': 'Not very wide', 'length': '2 meters'},
            {'name': 'Tesla', 'height': 'Medium height', 'width': 'Medium width', 'length': '2 meters'},
        ],
    },
]
yml_path = django_settings.BASE_DIR + '/demo_project/openapi-schema.yml'


def test_endpoints_static_schema(client, monkeypatch) -> None:  # noqa: TYP001
    """
    Asserts that the validate_response function validates correct schemas successfully.
    """
    monkeypatch.setattr(django_settings, 'SWAGGER_TESTER', {'PATH': yml_path})

    for item in good_test_data:
        response = client.get('/api/v1' + item['url'])  # type: ignore
        assert response.status_code == 200
        assert response.json() == item['expected_response']

        # Test Swagger documentation
        validate_response(response=response, method='GET', endpoint_url='/api/v1' + item['url'])  # type: ignore


def test_bad_endpoints_static_schema(client, monkeypatch, caplog) -> None:  # noqa: TYP001
    """
    Asserts that the validate_response function validates incorrect schemas successfully.
    """
    monkeypatch.setattr(django_settings, 'SWAGGER_TESTER', {'PATH': yml_path})
    for item in bad_test_data:
        response = client.get('/api/v1' + item['url'])  # type: ignore
        assert response.status_code == 200
        assert response.json() == item['expected_response']

        # Test Swagger documentation
        with pytest.raises(SwaggerDocumentationError, match='OpenAPI schema documentation suggests an empty list, '
                                                            'but the response contains list items'):
            validate_response(response=response, method='GET', endpoint_url='/api/v1' + item['url'])  # type: ignore
