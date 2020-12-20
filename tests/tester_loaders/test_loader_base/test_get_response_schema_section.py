from copy import deepcopy

import pytest
from tests.utils import MockRoute

from django_swagger_tester.exceptions import UndocumentedSchemaSectionError
from django_swagger_tester.loaders import _LoaderBase

response_200 = {
    'description': '',
    'schema': {
        'title': 'Success',
        'type': 'array',
        'items': {
            'title': 'Success',
            'type': 'object',
            'properties': {
                '1': {'description': 'description 1', 'type': 'string', 'example': 'example 1'},
                '2': {'description': 'description 2', 'type': 'string', 'example': 'value 2'},
                '3': {'description': 'description 3', 'type': 'string', 'example': 'value 3'},
            },
        },
    },
}

response_400 = {
    'description': '',
    'schema': {
        'title': 'Error',
        'type': 'object',
        'properties': {'error': {'description': 'Error response', 'type': 'string', 'example': 'Bad input'}},
    },
}
simple_response_schema = {
    'paths': {'test-endpoint': {'get': {'responses': {'200': response_200, '400': response_400}}}}
}


def test_succesful_load(monkeypatch):
    """
    Make sure the method returns the appropriate response schema section.
    """
    base = _LoaderBase()
    base.set_schema(simple_response_schema)
    monkeypatch.setattr(base, 'get_route', MockRoute)
    assert (
        base.get_response_schema_section(route='test-endpoint', method='get', status_code=200) == response_200['schema']
    )
    assert (
        base.get_response_schema_section(route='test-endpoint', method='get', status_code='200')
        == response_200['schema']
    )
    assert (
        base.get_response_schema_section(route='test-endpoint', method='get', status_code=400) == response_400['schema']
    )


def test_failed_index_paths(monkeypatch):
    """
    Make sure the right exception type is raised when indexing fails.
    """
    base = _LoaderBase()
    bad_schema = deepcopy(simple_response_schema)
    del bad_schema['paths']
    base.set_schema(bad_schema)
    monkeypatch.setattr(base, 'get_route', MockRoute)
    with pytest.raises(
        UndocumentedSchemaSectionError, match='Unsuccessfully tried to index the OpenAPI schema by `paths`'
    ):
        base.get_response_schema_section(route='test-endpoint', method='get', status_code=200)


def test_failed_index_route(monkeypatch):
    """
    Make sure the right exception type is raised when indexing fails.
    """
    base = _LoaderBase()
    bad_schema = deepcopy(simple_response_schema)
    del bad_schema['paths']['test-endpoint']
    base.set_schema(bad_schema)
    monkeypatch.setattr(base, 'get_route', MockRoute)
    with pytest.raises(
        UndocumentedSchemaSectionError, match='Unsuccessfully tried to index the OpenAPI schema by `test-endpoint`'
    ):
        base.get_response_schema_section(route='test-endpoint', method='get', status_code=200)


def test_failed_index_route_with_helper_text(monkeypatch):
    """
    Test helper texts.
    """
    base = _LoaderBase()
    bad_schema = deepcopy(simple_response_schema)
    del bad_schema['paths']['test-endpoint']
    bad_schema['paths']['other-endpoint'] = {}
    base.set_schema(bad_schema)
    monkeypatch.setattr(base, 'get_route', MockRoute)
    with pytest.raises(
        UndocumentedSchemaSectionError, match='Failed indexing schema.\n\nError: Unsuccessfully tried to index the OpenAPI schema by `test-endpoint`.\n\nFor debugging purposes, other valid routes include: \n\n\t• other-endpoint'
    ):
        base.get_response_schema_section(route='test-endpoint', method='get', status_code=200)


def test_failed_index_route_with_helper_text_and_middleware_warning(monkeypatch):
    """
    Test helper texts.
    """
    base = _LoaderBase()
    bad_schema = deepcopy(simple_response_schema)
    del bad_schema['paths']['test-endpoint']
    bad_schema['paths']['other-endpoint'] = {}
    base.set_schema(bad_schema)
    monkeypatch.setattr(base, 'get_route', MockRoute)
    with pytest.raises(
        UndocumentedSchemaSectionError,
        match=r'To skip validation for this route you can add `\^test-endpoint\$` to your VALIDATION_EXEMPT_URLS setting '
        'list in your SWAGGER_TESTER.MIDDLEWARE settings.',
    ):
        base.get_response_schema_section(
            route='test-endpoint', method='get', status_code=200, skip_validation_warning=True
        )


def test_failed_index_method(monkeypatch):
    """
    Make sure the right exception type is raised when indexing fails.
    """
    base = _LoaderBase()
    bad_schema = deepcopy(simple_response_schema)
    del bad_schema['paths']['test-endpoint']['get']
    base.set_schema(bad_schema)
    monkeypatch.setattr(base, 'get_route', MockRoute)
    with pytest.raises(
        UndocumentedSchemaSectionError, match='Unsuccessfully tried to index the OpenAPI schema by `get`'
    ):
        base.get_response_schema_section(route='test-endpoint', method='get', status_code=200)


def test_failed_index_method_with_helper_text(monkeypatch):
    """
    Make sure the right exception type is raised when indexing fails.
    """
    base = _LoaderBase()
    bad_schema = deepcopy(simple_response_schema)
    del bad_schema['paths']['test-endpoint']['get']
    bad_schema['paths']['test-endpoint']['post'] = {}
    bad_schema['paths']['test-endpoint']['put'] = {}
    base.set_schema(bad_schema)
    monkeypatch.setattr(base, 'get_route', MockRoute)
    with pytest.raises(UndocumentedSchemaSectionError, match='Available methods include: POST, PUT.'):
        base.get_response_schema_section(route='test-endpoint', method='get', status_code=200)


def test_failed_index_responses(monkeypatch):
    """
    Make sure the right exception type is raised when indexing fails.
    """
    base = _LoaderBase()
    bad_schema = deepcopy(simple_response_schema)
    del bad_schema['paths']['test-endpoint']['get']['responses']
    base.set_schema(bad_schema)
    monkeypatch.setattr(base, 'get_route', MockRoute)
    with pytest.raises(
        UndocumentedSchemaSectionError, match='Unsuccessfully tried to index the OpenAPI schema by `responses`'
    ):
        base.get_response_schema_section(route='test-endpoint', method='get', status_code=200)


def test_failed_index_status(monkeypatch):
    """
    Make sure the right exception type is raised when indexing fails.
    """
    base = _LoaderBase()
    bad_schema = deepcopy(simple_response_schema)
    del bad_schema['paths']['test-endpoint']['get']['responses']['200']
    del bad_schema['paths']['test-endpoint']['get']['responses']['400']
    base.set_schema(bad_schema)
    monkeypatch.setattr(base, 'get_route', MockRoute)
    with pytest.raises(
        UndocumentedSchemaSectionError,
        match='Unsuccessfully tried to index the OpenAPI schema by `200`. Is the `200` response documented?',
    ):
        base.get_response_schema_section(route='test-endpoint', method='get', status_code=200)


def test_failed_index_status_with_helper_text(monkeypatch):
    """
    Test helper text.
    """
    base = _LoaderBase()
    bad_schema = deepcopy(simple_response_schema)
    del bad_schema['paths']['test-endpoint']['get']['responses']['200']
    base.set_schema(bad_schema)
    monkeypatch.setattr(base, 'get_route', MockRoute)
    with pytest.raises(
        UndocumentedSchemaSectionError, match='Documented responses include: 400.  Is the `200` response documented?'
    ):
        base.get_response_schema_section(route='test-endpoint', method='get', status_code=200)
