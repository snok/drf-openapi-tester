from typing import Callable

import pytest

from openapi_tester import UndocumentedSchemaSectionError
from openapi_tester.schema_tester import SchemaTester
from tests.utils import response_factory

tester = SchemaTester()
parameterized_path = '/api/{version}/cars/correct'
de_parameterized_path = '/api/v1/cars/correct'
method = 'get'
status = '200'


def _mock_schema(schema) -> Callable:
    def _mocked():
        return schema

    return _mocked


def test_get_response_schema_section_success_scenario():
    schema = tester.loader.get_schema()

    for path, path_object in schema['paths'].items():
        for method, method_object in path_object.items():
            for status_code, responses_object in method_object['responses'].items():
                if hasattr(responses_object, 'content'):
                    schema_section = responses_object['content']['application/json']['schema']
                    response = response_factory(schema_section, path, method, status_code)
                    assert tester.get_response_schema_section(response) == schema_section
                    assert tester.get_response_schema_section(response) == schema_section


def test_get_response_schema_section_failure_scenario_undocumented_path(monkeypatch):
    schema = tester.loader.get_schema()
    schema_section = schema['paths'][parameterized_path][method]['responses'][status]['content']['application/json'][
        'schema'
    ]
    del schema['paths'][parameterized_path]
    monkeypatch.setattr(tester.loader, 'get_schema', _mock_schema(schema))
    response = response_factory(schema_section, de_parameterized_path, method, status)
    with pytest.raises(
        UndocumentedSchemaSectionError,
        match='Error: Unsuccessfully tried to index the OpenAPI schema by `/api/{version}/cars/correct`.',
    ):
        tester.get_response_schema_section(response)


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
