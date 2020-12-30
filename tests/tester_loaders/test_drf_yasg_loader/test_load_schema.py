from django_openapi_response_tester.loaders import DrfYasgSchemaLoader


def test_successful_parse_documented_endpoints(monkeypatch) -> None:
    """
    Asserts that a schema section is returned successfully.
    """
    base = DrfYasgSchemaLoader()
    base.get_schema()
    base.get_response_schema_section(route='/api/v1/cars/correct/', method='GET', status_code=200)
