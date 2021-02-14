import pytest

from openapi_tester.loaders import DrfSpectacularSchemaLoader, DrfYasgSchemaLoader, StaticSchemaLoader
from tests.utils import TEST_ROOT

yaml_schema_path = str(TEST_ROOT) + "/schemas/test_project_schema.yaml"
json_schema_path = str(TEST_ROOT) + "/schemas/test_project_schema.json"
loaders = [
    StaticSchemaLoader(yaml_schema_path),
    StaticSchemaLoader(json_schema_path),
    DrfYasgSchemaLoader(),
    DrfSpectacularSchemaLoader(),
]


@pytest.mark.parametrize("loader", loaders)
def test_loader_get_schema(loader):
    loader.get_schema()  # runs internal validation


@pytest.mark.parametrize("loader", loaders)
def test_loader_get_route(loader):
    assert loader.parameterize_path("/api/v1/items/") == "/api/{version}/items"
    assert loader.parameterize_path("/api/v1/items") == "/api/{version}/items"
    assert loader.parameterize_path("api/v1/items/") == "/api/{version}/items"
    assert loader.parameterize_path("api/v1/items") == "/api/{version}/items"
    assert loader.parameterize_path("/api/v1/snake-case/") == "/api/{version}/snake-case/"
    assert loader.parameterize_path("/api/v1/snake-case") == "/api/{version}/snake-case/"
    assert loader.parameterize_path("api/v1/snake-case/") == "/api/{version}/snake-case/"
    assert loader.parameterize_path("api/v1/snake-case") == "/api/{version}/snake-case/"


@pytest.mark.parametrize("loader", loaders)
def test_loader_resolve_path(loader):
    assert loader.resolve_path("/api/v1/cars/correct") is not None

    with pytest.raises(
        ValueError, match="Could not resolve path `/api/v1/blars/correct`.\n\nDid you mean one of these?"
    ):
        loader.resolve_path("/api/v1/blars/correct")
