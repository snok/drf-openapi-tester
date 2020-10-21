import pytest
from django.core.exceptions import ImproperlyConfigured

from django_swagger_tester.loaders import _LoaderBase

simple_ref_schema = {
    'paths': {
        'test-endpoint': {
            'post': {
                'parameters': [{'name': 'data', 'in': 'body', 'required': True, 'schema': {'$ref': '#/definitions/Test'}}]
            }
        }
    },
    'definitions': {
        'Test': {
            'required': ['testParameter'],
            'type': 'object',
            'properties': {
                'testParameter': {'title': 'This is a test ref', 'type': 'string', 'maxLength': 10, 'minLength': 1}
            },
            'example': {'testParameter': 'test value'},
        }
    },
}
simple_ref_replaced_parameters = {
    'name': 'data',
    'in': 'body',
    'required': True,
    'schema': {
        'required': ['testParameter'],
        'type': 'object',
        'properties': {'testParameter': {'title': 'This is a test ref', 'type': 'string', 'maxLength': 10, 'minLength': 1}},
        'example': {'testParameter': 'test value'},
    },
}


def test_set_schema_with_refs():
    """
    $ref values should be replaced when setting schema.
    """
    base = _LoaderBase()
    base.set_schema(simple_ref_schema)
    assert base.original_schema == simple_ref_schema
    assert base.schema['paths']['test-endpoint']['post']['parameters'][0] == simple_ref_replaced_parameters


def test_get_schema_when_schema_has_been_set():
    """
    get_schema should return self.schema if schema is set.
    """
    base = _LoaderBase()
    base.set_schema(simple_ref_schema)
    assert base.get_schema()['paths']['test-endpoint']['post']['parameters'][0] == simple_ref_replaced_parameters


def test_get_schema_when_no_schema_has_been_loaded():
    """
    get_schema should try to call self.load_schema if self.schema is not set, and this method is required to overwrite,
    so for the base-class this should raise an error.
    """
    base = _LoaderBase()
    with pytest.raises(NotImplementedError, match='The `load_schema` method has to be overwritten.'):
        base.get_schema()


def test_call_validation():
    """
    The base class should contain a self.validation method to optionally overwrite.
    """
    base = _LoaderBase()
    assert base.validation() is None


def test_get_route():
    base = _LoaderBase()
    assert base.get_route('/api/v1/items/').get_path() == '/api/{version}/items'
    assert base.get_route('/api/v1/items').get_path() == '/api/{version}/items'
    assert base.get_route('api/v1/items/').get_path() == '/api/{version}/items'
    assert base.get_route('api/v1/items').get_path() == '/api/{version}/items'
    assert base.get_route('/api/v1/snake-case/').get_path() == '/api/{version}/snake-case/'
    assert base.get_route('/api/v1/snake-case').get_path() == '/api/{version}/snake-case/'
    assert base.get_route('api/v1/snake-case/').get_path() == '/api/{version}/snake-case/'
    assert base.get_route('api/v1/snake-case').get_path() == '/api/{version}/snake-case/'
