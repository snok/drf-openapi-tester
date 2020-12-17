from django.conf import settings as django_settings

from django_swagger_tester.loaders import StaticSchemaLoader
from django_swagger_tester.testing import validate_response

good_test_data = [
    {
        'url': '/cars/correct',
        'expected_response': [
            {'name': 'Saab', 'color': 'Yellow', 'height': 'Medium height', 'width': 'Very wide', 'length': '2 meters'},
            {'name': 'Volvo', 'color': 'Red', 'height': 'Medium height', 'width': 'Not wide', 'length': '2 meters'},
            {'name': 'Tesla', 'color': 'black', 'height': 'Medium height', 'width': 'Wide', 'length': '2 meters'},
        ],
    },
    {
        'url': '/trucks/correct',
        'expected_response': [
            {'name': 'Saab', 'color': 'Yellow', 'height': 'Medium height', 'width': 'Very wide', 'length': '2 meters'},
            {'name': 'Volvo', 'color': 'Red', 'height': 'Medium height', 'width': 'Not wide', 'length': '2 meters'},
            {'name': 'Tesla', 'color': 'black', 'height': 'Medium height', 'width': 'Wide', 'length': '2 meters'},
        ],
    },
    {
        'url': '/i18n',
        'lang': 'en',
        'expected_response': {
            'languages': ['French', 'Spanish', 'Greek', 'Italian', 'Portuguese'],
        },
    },
    {
        'url': '/i18n',
        'lang': 'de',
        'expected_response': {
            'languages': ['Französisch', 'Spanisch', 'Griechisch', 'Italienisch', 'Portugiesisch'],
        },
    },
]

bad_test_data = [
    {
        'url': '/cars/incorrect',
        'expected_response': [
            {'name': 'Saab', 'color': 'Yellow', 'height': 'Medium height'},
            {'name': 'Volvo', 'color': 'Red', 'width': 'Not very wide', 'length': '2 meters'},
            {'name': 'Tesla', 'height': 'Medium height', 'width': 'Medium width', 'length': '2 meters'},
        ],
    },
    {
        'url': '/trucks/incorrect',
        'expected_response': [
            {'name': 'Saab', 'color': 'Yellow', 'height': 'Medium height'},
            {'name': 'Volvo', 'color': 'Red', 'width': 'Not very wide', 'length': '2 meters'},
            {'name': 'Tesla', 'height': 'Medium height', 'width': 'Medium width', 'length': '2 meters'},
        ],
    },
]
yml_path = str(django_settings.BASE_DIR) + '/static_schemas/openapi-schema.yml'


def test_endpoints_static_schema(client, monkeypatch, transactional_db) -> None:  # noqa: TYP001
    """
    Asserts that the validate_response function validates correct schemas successfully.
    """
    monkeypatch.setattr(django_settings, 'SWAGGER_TESTER', {'PATH': yml_path, 'SCHEMA_LOADER': StaticSchemaLoader})
    for item in good_test_data:
        lang_prefix = '/' + item['lang'] if 'lang' in item else ''
        url = lang_prefix + '/api/v1' + item['url']
        response = client.get(url)
        assert response.status_code == 200
        assert response.json() == item['expected_response']
        validate_response(response=response, method='GET', route=url)
