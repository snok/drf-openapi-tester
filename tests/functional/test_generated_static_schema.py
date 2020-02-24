from openapi_tester import validate_schema

test_data = [
    {
        'url': '/cars/correct/',
        'expected_response': [
            {'name': 'Saab', 'color': 'Yellow', 'height': 'Medium height', 'width': 'Very wide', 'length': '2 meters'},
            {'name': 'Volvo', 'color': 'Red', 'height': 'Medium height', 'width': 'Not wide', 'length': '2 meters'},
            {'name': 'Tesla', 'color': 'black', 'height': 'Medium height', 'width': 'Wide', 'length': '2 meters'},
        ],
    },
    {
        'url': '/cars/incorrect/',
        'expected_response': [
            {'name': 'Saab', 'color': 'Yellow', 'height': 'Medium height'},
            {'name': 'Volvo', 'color': 'Red', 'width': 'Not very wide', 'length': '2 meters'},
            {'name': 'Tesla', 'height': 'Medium height', 'width': 'Medium width', 'length': '2 meters'},
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
    {
        'url': '/trucks/incorrect/',
        'expected_response': [
            {'name': 'Saab', 'color': 'Yellow', 'height': 'Medium height'},
            {'name': 'Volvo', 'color': 'Red', 'width': 'Not very wide', 'length': '2 meters'},
            {'name': 'Tesla', 'height': 'Medium height', 'width': 'Medium width', 'length': '2 meters'},
        ],
    },
]


def test_endpoints_static_schema(client, monkeypatch) -> None:  # noqa: TYP001
    """
    Asserts that the validate_schema function validates correct schemas successfully.
    """
    from django.conf import settings as openapi_settings

    monkeypatch.setattr(
        openapi_settings,
        'OPENAPI_TESTER',
        {'SCHEMA': 'static', 'CASE': 'camel case', 'path': openapi_settings.BASE_DIR + '/drf_yasg/openapi-schema.yml'},
    )
    for item in test_data:
        response = client.get('/api/v1' + item['url'])
        assert response.status_code == 200
        assert response.json() == item['expected_response']

        # Test Swagger documentation
        validate_schema(response, 'GET', '/api/v1' + item['url'])
