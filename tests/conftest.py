from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING, Callable
from unittest.mock import MagicMock

import pytest
from rest_framework.response import Response

from tests.schema_converter import SchemaToPythonConverter
from tests.utils import TEST_ROOT

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture()
def pets_api_schema() -> Path:
    return TEST_ROOT / "schemas" / "openapi_v3_reference_schema.yaml"


@pytest.fixture()
def pets_post_request():
    request_body = MagicMock()
    request_body.read.return_value = b'{"name": "doggie", "tag": "dog"}'
    return {
        "PATH_INFO": "/api/pets",
        "REQUEST_METHOD": "POST",
        "SERVER_PORT": "80",
        "wsgi.url_scheme": "http",
        "CONTENT_LENGTH": "70",
        "CONTENT_TYPE": "application/json",
        "wsgi.input": request_body,
        "QUERY_STRING": "",
    }


@pytest.fixture()
def invalid_pets_post_request():
    request_body = MagicMock()
    request_body.read.return_value = b'{"surname": "doggie", "species": "dog"}'
    return {
        "PATH_INFO": "/api/pets",
        "REQUEST_METHOD": "POST",
        "SERVER_PORT": "80",
        "wsgi.url_scheme": "http",
        "CONTENT_LENGTH": "70",
        "CONTENT_TYPE": "application/json",
        "wsgi.input": request_body,
        "QUERY_STRING": "",
    }


@pytest.fixture()
def response_factory() -> Callable:
    def response(
        schema: dict | None,
        url_fragment: str,
        method: str,
        status_code: int | str = 200,
        response_body: dict | None = None,
    ) -> Response:
        converted_schema = None
        if schema:
            converted_schema = SchemaToPythonConverter(deepcopy(schema)).result
        response = Response(status=int(status_code), data=converted_schema)
        response.request = {"REQUEST_METHOD": method, "PATH_INFO": url_fragment}  # type: ignore
        if schema:
            response.json = lambda: converted_schema  # type: ignore
        elif response_body:
            response.request["CONTENT_LENGTH"] = len(response_body)  # type: ignore
            response.request["CONTENT_TYPE"] = "application/json"  # type: ignore
            response.request["wsgi.input"] = response_body  # type: ignore
            response.renderer_context = {"request": MagicMock(data=response_body)}  # type: ignore
        return response

    return response
