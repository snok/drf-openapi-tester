import pytest
from django.core.exceptions import ImproperlyConfigured
from openapi_spec_validator import openapi_v2_spec_validator, openapi_v3_spec_validator

from openapi_tester.loaders import BaseSchemaLoader, DrfSpectacularSchemaLoader, DrfYasgSchemaLoader, StaticSchemaLoader
from tests.utils import CURRENT_PATH

simple_ref_schema = {
    'swagger': '2.0',
    'info': {'title': 'specs-title', 'version': '1.0.0'},
    'paths': {
        '/test-endpoint/': {
            'post': {
                'parameters': [
                    {'name': 'data', 'in': 'body', 'required': True, 'schema': {'$ref': '#/definitions/Test'}}
                ],
                'responses': {'204': {'description': ''}},
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
        'properties': {
            'testParameter': {'title': 'This is a test ref', 'type': 'string', 'maxLength': 10, 'minLength': 1}
        },
        'example': {'testParameter': 'test value'},
    },
}


def test_base_dereference_schema():
    loader = BaseSchemaLoader()
    with pytest.raises(NotImplementedError):
        loader.get_schema()
    loader.set_schema(simple_ref_schema)
    assert loader.schema['paths']['/test-endpoint/']['post']['parameters'][0] == simple_ref_replaced_parameters
    assert loader.get_schema()['paths']['/test-endpoint/']['post']['parameters'][0] == simple_ref_replaced_parameters


def test_drf_spectacular_get_schemas():
    loader = DrfSpectacularSchemaLoader()
    schema = loader.get_schema()
    openapi_v3_spec_validator.validate(schema)


def test_drf_yasg_get_schemas():
    loader = DrfYasgSchemaLoader()
    schema = loader.get_schema()
    openapi_v2_spec_validator.validate(schema)


def test_static_get_schema():
    for ext in ['yml', 'json']:
        loader = StaticSchemaLoader(str(CURRENT_PATH) + f'/schemas/test_project_schema.{ext}')
        schema = loader.get_schema()
        openapi_v3_spec_validator.validate(schema)

    loader = StaticSchemaLoader(str(CURRENT_PATH) + '/schemas/lol.fun')
    with pytest.raises(ImproperlyConfigured):
        loader.get_schema()


def test_base_loader_get_route():
    for _loader in [BaseSchemaLoader, DrfYasgSchemaLoader, DrfSpectacularSchemaLoader]:
        loader = _loader()
        assert loader.get_route('/api/v1/items/') == '/api/{version}/items'
        assert loader.get_route('/api/v1/items') == '/api/{version}/items'
        assert loader.get_route('api/v1/items/') == '/api/{version}/items'
        assert loader.get_route('api/v1/items') == '/api/{version}/items'
        assert loader.get_route('/api/v1/snake-case/') == '/api/{version}/snake-case/'
        assert loader.get_route('/api/v1/snake-case') == '/api/{version}/snake-case/'
        assert loader.get_route('api/v1/snake-case/') == '/api/{version}/snake-case/'
        assert loader.get_route('api/v1/snake-case') == '/api/{version}/snake-case/'
