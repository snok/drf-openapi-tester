from django_swagger_tester.loaders import DrfSpectacularSchemaLoader


def test_successful_parse_documented_endpoints() -> None:
    """
    Asserts that a schema section is returned successfully.
    """
    base = DrfSpectacularSchemaLoader()
    base.get_schema()
    base.get_response_schema_section(route='/api/v1/cars/correct/', method='GET', status_code=200)
