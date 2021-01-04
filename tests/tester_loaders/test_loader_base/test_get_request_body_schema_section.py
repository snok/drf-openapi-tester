from copy import deepcopy

import pytest

from response_tester.exceptions import UndocumentedSchemaSectionError
from response_tester.loaders import BaseSchemaLoader
from tests.utils import MockRoute

request_body = {
    'required': ['testParameter'],
    'type': 'object',
    'properties': {'testParameter': {'title': 'Test parameter', 'type': 'string', 'maxLength': 10, 'minLength': 1}},
    'example': {'testParameter': 'test'},
}
simple_request_body_schema = {
    'paths': {
        'test-endpoint': {
            'post': {
                'parameters': [
                    {'name': 'data', 'in': 'body', 'required': True, 'schema': {'$ref': '#/definitions/Test'}}
                ],
                'tags': ['v1'],
            },
            'parameters': [],
        }
    },
    'definitions': {
        'Test': {
            'required': ['testParameter'],
            'type': 'object',
            'properties': {
                'testParameter': {'title': 'Test parameter', 'type': 'string', 'maxLength': 10, 'minLength': 1}
            },
            'example': {'testParameter': 'test'},
        }
    },
}


def test_successful_load(monkeypatch):
    """
    Make sure the API works.
    """
    base = BaseSchemaLoader()
    base.set_schema(simple_request_body_schema)
    monkeypatch.setattr(base, 'get_route', MockRoute)
    assert base.get_request_body_schema_section(route='test-endpoint', method='post') == request_body


def test_fail_indexing_paths(monkeypatch):
    base = BaseSchemaLoader()
    bad_schema = deepcopy(simple_request_body_schema)
    del bad_schema['paths']
    base.set_schema(bad_schema)
    monkeypatch.setattr(base, 'get_route', MockRoute)
    with pytest.raises(
        UndocumentedSchemaSectionError, match='Unsuccessfully tried to index the OpenAPI schema by `paths`'
    ):
        base.get_request_body_schema_section(route='test-endpoint', method='post')


def test_fail_indexing_route(monkeypatch):
    base = BaseSchemaLoader()
    bad_schema = deepcopy(simple_request_body_schema)
    del bad_schema['paths']['test-endpoint']
    base.set_schema(bad_schema)
    monkeypatch.setattr(base, 'get_route', MockRoute)
    with pytest.raises(
        UndocumentedSchemaSectionError, match='Unsuccessfully tried to index the OpenAPI schema by `test-endpoint`'
    ):
        base.get_request_body_schema_section(route='test-endpoint', method='post')


def test_fail_indexing_route_with_helper_text(monkeypatch):
    base = BaseSchemaLoader()
    bad_schema = deepcopy(simple_request_body_schema)
    del bad_schema['paths']['test-endpoint']
    bad_schema['paths']['other-endpoint'] = {}
    bad_schema['paths']['third-endpoint'] = {}
    base.set_schema(bad_schema)
    monkeypatch.setattr(base, 'get_route', MockRoute)
    with pytest.raises(
        UndocumentedSchemaSectionError,
        match='Failed indexing schema.\n\nError: Unsuccessfully tried to index'
        ' the OpenAPI schema by `test-endpoint`.\n\nFor debugging purpose'
        's, other valid routes include: \n\n\t• other-endpoint,\n\t• '
        'third-endpoint',
    ):
        base.get_request_body_schema_section(route='test-endpoint', method='post')


def test_fail_indexing_method(monkeypatch):
    base = BaseSchemaLoader()
    bad_schema = deepcopy(simple_request_body_schema)
    del bad_schema['paths']['test-endpoint']['post']
    base.set_schema(bad_schema)
    monkeypatch.setattr(base, 'get_route', MockRoute)
    with pytest.raises(
        UndocumentedSchemaSectionError, match='Unsuccessfully tried to index the OpenAPI schema by `post`.'
    ):
        base.get_request_body_schema_section(route='test-endpoint', method='post')


def test_fail_indexing_method_with_helper_text(monkeypatch):
    base = BaseSchemaLoader()
    base.set_schema(simple_request_body_schema)
    monkeypatch.setattr(base, 'get_route', MockRoute)
    with pytest.raises(UndocumentedSchemaSectionError, match='Available methods include: POST.'):
        base.get_request_body_schema_section(route='test-endpoint', method='put')


def test_fail_indexing_parameters(monkeypatch):
    base = BaseSchemaLoader()
    bad_schema = deepcopy(simple_request_body_schema)
    del bad_schema['paths']['test-endpoint']['post']['parameters']
    base.set_schema(bad_schema)
    monkeypatch.setattr(base, 'get_route', MockRoute)
    with pytest.raises(
        UndocumentedSchemaSectionError, match='Unsuccessfully tried to index the OpenAPI schema by `parameters`.'
    ):
        base.get_request_body_schema_section(route='test-endpoint', method='post')


def test_fail_getting_parameter(monkeypatch):
    base = BaseSchemaLoader()
    bad_schema = deepcopy(simple_request_body_schema)
    bad_schema['paths']['test-endpoint']['post']['parameters'] = []
    base.set_schema(bad_schema)
    monkeypatch.setattr(base, 'get_route', MockRoute)
    with pytest.raises(
        UndocumentedSchemaSectionError,
        match='Request body does not seem to be documented. '
        '`Parameters` is empty for path `test-endpoint` and method `post`',
    ):
        base.get_request_body_schema_section(route='test-endpoint', method='post')


def test_no_request_body(monkeypatch):
    base = BaseSchemaLoader()
    bad_schema = deepcopy(simple_request_body_schema)
    bad_schema['paths']['test-endpoint']['post']['parameters'][0]['in'] = 'path'
    base.set_schema(bad_schema)
    monkeypatch.setattr(base, 'get_route', MockRoute)
    with pytest.raises(
        UndocumentedSchemaSectionError,
        match='There is no in-body request body documented for route `test-endpoint` and method `post`',
    ):
        base.get_request_body_schema_section(route='test-endpoint', method='post')


def test_get_request_body_example(monkeypatch):
    """
    Makes sure we're able to generate an example value for the documented request body, with or without example values.
    """
    base = BaseSchemaLoader()
    monkeypatch.setattr(base, 'get_route', MockRoute)
    base.set_schema(simple_request_body_schema)
    assert base.get_request_body_example(route='test-endpoint', method='post') == {'testParameter': 'test'}

    schema_without_example = base.dereference_schema(deepcopy(simple_request_body_schema))
    del schema_without_example['paths']['test-endpoint']['post']['parameters'][0]['schema']['example']
    base.set_schema(schema_without_example)
    assert base.get_request_body_example(route='test-endpoint', method='post') == {'testParameter': 'string'}
