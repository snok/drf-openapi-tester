from django.conf import settings as django_settings
from django_swagger_tester.loaders import StaticSchemaLoader
from django_swagger_tester.testing import validate_response
from tests.test_testers.test_validate_response import GOOD_TEST_DATA

yml_path = str(django_settings.BASE_DIR) + '/openapi-schema.yml'


def test_endpoints_static_schema(client, monkeypatch, transactional_db) -> None:  # noqa: TYP001
    """
    Asserts that the validate_response function validates correct schemas successfully.
    """
    monkeypatch.setattr(django_settings, 'SWAGGER_TESTER', {'PATH': yml_path, 'SCHEMA_LOADER': StaticSchemaLoader})
    for item in GOOD_TEST_DATA:
        route = f"/api/v1{item['url']}"
        response = client.get(route)
        assert response.status_code == 200
        assert response.json() == item['expected_response']
        validate_response(response=response, method='GET', route=route)


