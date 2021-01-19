import pytest
from django.core.exceptions import ImproperlyConfigured

from openapi_tester.loaders import BaseSchemaLoader, DrfSpectacularSchemaLoader, DrfYasgSchemaLoader, StaticSchemaLoader
from tests.utils import CURRENT_PATH


def test_drf_spectacular_get_schemas():
    loader = DrfSpectacularSchemaLoader()
    loader.get_schema()  # runs internal validation


def test_drf_yasg_get_schemas():
    loader = DrfYasgSchemaLoader()
    loader.get_schema()  # runs internal validation


def test_static_get_schema():
    for ext in ['yaml', 'json']:
        loader = StaticSchemaLoader(str(CURRENT_PATH) + f'/schemas/test_project_schema.{ext}')
        loader.get_schema()  # runs internal validation

    loader = StaticSchemaLoader(str(CURRENT_PATH) + '/schemas/lol.fun')
    with pytest.raises(ImproperlyConfigured):
        loader.get_schema()


def test_base_loader_get_route():
    for _loader in [BaseSchemaLoader, DrfYasgSchemaLoader, DrfSpectacularSchemaLoader]:
        loader = _loader()
        assert loader.parameterize_path('/api/v1/items/') == '/api/{version}/items'
        assert loader.parameterize_path('/api/v1/items') == '/api/{version}/items'
        assert loader.parameterize_path('api/v1/items/') == '/api/{version}/items'
        assert loader.parameterize_path('api/v1/items') == '/api/{version}/items'
        assert loader.parameterize_path('/api/v1/snake-case/') == '/api/{version}/snake-case/'
        assert loader.parameterize_path('/api/v1/snake-case') == '/api/{version}/snake-case/'
        assert loader.parameterize_path('api/v1/snake-case/') == '/api/{version}/snake-case/'
        assert loader.parameterize_path('api/v1/snake-case') == '/api/{version}/snake-case/'
