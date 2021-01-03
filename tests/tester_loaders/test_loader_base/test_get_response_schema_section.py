import pytest

from openapi_tester.exceptions import UndocumentedSchemaSectionError
from openapi_tester.loaders import BaseSchemaLoader
from tests.utils import MockRoute, ret_schema

route = '/api/v1/cars/correct'
method = 'get'
code = '200'
schema_object = ret_schema()
response_200 = schema_object['paths'][route][method]['responses'][code]['content']['application/json']['schema']


def test_succesful_load(monkeypatch):
    """
    Make sure the method returns the appropriate response schema section.
    """
    base = BaseSchemaLoader()
    base.set_schema(schema_object)
    monkeypatch.setattr(base, 'get_route', MockRoute)
    assert base.get_response_schema_section(route=route, method=method, status_code=int(code)) == response_200
    assert base.get_response_schema_section(route=route, method=method, status_code=code) == response_200


def test_failed_index_route(monkeypatch):

    base = BaseSchemaLoader()
    base.set_schema(schema_object)
    monkeypatch.setattr(base, 'get_route', MockRoute)
    with pytest.raises(
        UndocumentedSchemaSectionError, match='Unsuccessfully tried to index the OpenAPI schema by `some-route`'
    ):
        base.get_response_schema_section(route='some-route', method=method, status_code=code)


def test_failed_index_route_helper_text(monkeypatch):

    base = BaseSchemaLoader()
    base.set_schema(schema_object)
    monkeypatch.setattr(base, 'get_route', MockRoute)
    with pytest.raises(
        UndocumentedSchemaSectionError,
        match='Failed indexing schema.\n\nError: Unsuccessfully tried to index the OpenAPI schema by `some-route`. \n\nFor debugging purposes, other valid routes include: \n\n\t• /api/v1/cars/correct,\n\t• /api/v1/cars/incorrect,\n\t• /api/v1/trucks/correct,\n\t• /api/v1/trucks/incorrect,\n\t• /{language}/api/v1/i18n',
    ):
        base.get_response_schema_section(route='some-route', method=method, status_code=code)


def test_failed_index_method(monkeypatch):

    base = BaseSchemaLoader()
    base.set_schema(schema_object)
    monkeypatch.setattr(base, 'get_route', MockRoute)
    with pytest.raises(
        UndocumentedSchemaSectionError, match='Unsuccessfully tried to index the OpenAPI schema by `patch`'
    ):
        base.get_response_schema_section(route=route, method='patch', status_code=code)


def test_failed_index_method_with_helper_text(monkeypatch):

    base = BaseSchemaLoader()
    base.set_schema(schema_object)
    monkeypatch.setattr(base, 'get_route', MockRoute)
    with pytest.raises(
        UndocumentedSchemaSectionError,
        match='Failed indexing schema.\n\nError: Unsuccessfully tried to index the OpenAPI schema by `patch`. \n\nAvailable methods include: GET, POST, PUT, DELETE.',
    ):
        base.get_response_schema_section(route=route, method='patch', status_code=code)


def test_failed_index_status_with_helper_text(monkeypatch):

    base = BaseSchemaLoader()
    base.set_schema(schema_object)
    monkeypatch.setattr(base, 'get_route', MockRoute)
    with pytest.raises(
        UndocumentedSchemaSectionError, match='Documented responses include: 200.  Is the `400` response documented?'
    ):
        base.get_response_schema_section(route=route, method=method, status_code='400')
