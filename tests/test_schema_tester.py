from openapi_tester.schema_tester import SchemaTester
from tests.utils import response_factory


def test_succesful_load():
    tester = SchemaTester()
    schema = tester.loader.get_schema()

    for path, path_object in schema['paths'].items():
        for method, method_object in path_object.items():
            for status_code, responses_object in method_object['responses'].items():
                if hasattr(responses_object, 'content'):
                    schema_section = responses_object['content']['application/json']['schema']
                    response = response_factory(schema_section, path, method, status_code)
                    assert tester.get_response_schema_section(response) == schema_section
                    assert tester.get_response_schema_section(response) == schema_section


# def test_failed_index_route(monkeypatch):
#     base = BaseSchemaLoader()
#     base.set_schema(schema_object)
#     monkeypatch.setattr(base, 'get_route', MockRoute)
#     with pytest.raises(
#         UndocumentedSchemaSectionError,
#         match='Failed indexing schema.\n\nError: Unsuccessfully tried to index the OpenAPI schema by `some-route`. \n\nFor debugging purposes, other valid routes include: \n\n\t• /api/v1/cars/correct,\n\t• /api/v1/cars/incorrect,\n\t• /api/v1/trucks/correct,\n\t• /api/v1/trucks/incorrect,\n\t• /{language}/api/v1/i18n',
#     ):
#         base.get_response_schema_section(route='some-route', method=method, status_code=code)
#
#
# def test_failed_index_method(monkeypatch):
#     base = BaseSchemaLoader()
#     base.set_schema(schema_object)
#     monkeypatch.setattr(base, 'get_route', MockRoute)
#     with pytest.raises(
#         UndocumentedSchemaSectionError,
#         match='Failed indexing schema.\n\nError: Unsuccessfully tried to index the OpenAPI schema by `patch`. \n\nAvailable methods include: GET, POST, PUT, DELETE.',
#     ):
#         base.get_response_schema_section(route=route, method='patch', status_code=code)
#
#
# def test_failed_index_status(monkeypatch):
#     base = BaseSchemaLoader()
#     base.set_schema(schema_object)
#     monkeypatch.setattr(base, 'get_route', MockRoute)
#     with pytest.raises(
#         UndocumentedSchemaSectionError, match='Documented responses include: 200.  Is the `400` response documented?'
#     ):
#         base.get_response_schema_section(route=route, method=method, status_code='400')
