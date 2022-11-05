from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from openapi_tester.loaders import (
    DrfSpectacularSchemaLoader,
    DrfYasgSchemaLoader,
    StaticSchemaLoader,
    UrlStaticSchemaLoader,
)
from tests.utils import TEST_ROOT, get_schema_content

yaml_schema_path = str(TEST_ROOT) + "/schemas/manual_reference_schema.yaml"
json_schema_path = str(TEST_ROOT) + "/schemas/manual_reference_schema.json"

loaders = [
    StaticSchemaLoader(yaml_schema_path, field_key_map={"language": "en"}),
    StaticSchemaLoader(json_schema_path, field_key_map={"language": "en"}),
    DrfYasgSchemaLoader(field_key_map={"language": "en"}),
    DrfSpectacularSchemaLoader(field_key_map={"language": "en"}),
]
static_schema_loaders = [
    StaticSchemaLoader(yaml_schema_path, field_key_map={"language": "en"}),
    StaticSchemaLoader(json_schema_path, field_key_map={"language": "en"}),
]


@pytest.mark.parametrize("loader", loaders)
def test_loader_get_schema(loader):
    loader.get_schema()  # runs internal validation


def test_url_schema_loader():
    test_schema_url = "http://schemas:8080/test/schema.yaml"
    schema_loader = UrlStaticSchemaLoader(test_schema_url)
    schema_content = get_schema_content(TEST_ROOT / "schemas" / "any_of_one_of_test_schema.yaml")

    with patch("openapi_tester.loaders.requests.get") as mocked_get_request:
        mocked_get_request.return_value = Mock(content=schema_content)
        loaded_schema = schema_loader.load_schema()

    assert type(loaded_schema) == dict
    assert loaded_schema["openapi"] == "3.0.0"
    assert loaded_schema["info"]["title"] == "Swagger Petstore"


@pytest.mark.parametrize("loader", loaders)
def test_loader_get_route(loader):
    assert loader.resolve_path("/api/v1/items/", "get")[0] == "/api/{version}/items"
    assert loader.resolve_path("/api/v1/items", "get")[0] == "/api/{version}/items"
    assert loader.resolve_path("api/v1/items/", "get")[0] == "/api/{version}/items"
    assert loader.resolve_path("api/v1/items", "get")[0] == "/api/{version}/items"
    assert loader.resolve_path("/api/v1/snake-case/", "get")[0] == "/api/{version}/snake-case/"
    assert loader.resolve_path("/api/v1/snake-case", "get")[0] == "/api/{version}/snake-case/"
    assert loader.resolve_path("api/v1/snake-case/", "get")[0] == "/api/{version}/snake-case/"
    assert loader.resolve_path("api/v1/snake-case", "get")[0] == "/api/{version}/snake-case/"
    with pytest.raises(ValueError, match="Could not resolve path `test`"):
        assert loader.resolve_path("test", "get")


@pytest.mark.parametrize("loader", loaders)
def test_loader_resolve_path(loader):
    assert loader.resolve_path("/api/v1/cars/correct", "get") is not None

    with pytest.raises(
        ValueError, match="Could not resolve path `/api/v1/blars/correct`.\n\nDid you mean one of these?"
    ):
        loader.resolve_path("/api/v1/blars/correct", "get")


@pytest.mark.parametrize("loader", static_schema_loaders)
def test_static_loader_resolve_nested_route(loader):
    assert (
        loader.resolve_path("/api/v1/categories/1/subcategories/1/", "get")[0]
        == "/api/{version}/categories/{category_pk}/subcategories/{subcategory_pk}/"
    )
