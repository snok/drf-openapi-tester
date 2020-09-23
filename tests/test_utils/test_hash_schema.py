from django_swagger_tester.loaders import DrfSpectacularSchemaLoader, DrfYasgSchemaLoader, StaticSchemaLoader
from django_swagger_tester.utils import hash_schema
from tests.utils import yml_path


def test_drf_spectacular_schema_hash():
    """
    Verify that validation runs successfully for the demo project.
    """
    base = DrfSpectacularSchemaLoader()
    base.get_schema()
    schema = base.get_response_schema_section('/api/v1/cars/correct', method='GET', status_code=200)
    assert hash_schema(schema) == hash_schema(schema)


def test_drf_yasg_schema_hash(monkeypatch) -> None:
    """
    Asserts that a schema section is returned successfully.
    """
    base = DrfYasgSchemaLoader()
    base.get_schema()
    schema = base.get_response_schema_section('/api/v1/cars/correct', method='GET', status_code=200)
    assert hash_schema(schema) == hash_schema(schema)


def test_static_schema_hash(monkeypatch) -> None:
    """
    Tests that a file is fetched successfully.
    """
    base = StaticSchemaLoader()
    base.set_path(yml_path)
    base.get_schema()
    schema = base.get_response_schema_section('/api/v1/cars/correct', method='GET', status_code=200)
    assert hash_schema(schema) == hash_schema(schema)
