import json
from pathlib import Path
from typing import Any, Callable, Generator, Optional, Tuple, Union

import yaml
from rest_framework.response import Response

from openapi_tester.schema_converter import SchemaToPythonConverter

TEST_ROOT = Path(__file__).resolve(strict=True).parent


def load_schema(file_name: str) -> dict:
    with open(str(TEST_ROOT) + f"/schemas/{file_name}") as f:
        content = f.read()
        if "json" in file_name:
            return json.loads(content)
        else:
            return yaml.load(content, Loader=yaml.FullLoader)


def response_factory(schema: dict, url_fragment: str, method: str, status_code: Union[int, str] = 200) -> Response:
    converted_schema = SchemaToPythonConverter(schema, with_faker=True).result
    response = Response(status=int(status_code), data=converted_schema)
    response.request = dict(REQUEST_METHOD=method, PATH_INFO=url_fragment)
    response.json = lambda: converted_schema  # type: ignore
    return response


def iterate_schema(schema: dict) -> Generator[Tuple[Optional[dict], Optional[Response], str], None, None]:
    for url_fragment, path_object in schema["paths"].items():
        for method, method_object in path_object.items():
            if method.lower() != "parameters":
                for status_code, responses_object in method_object["responses"].items():
                    if status_code == "default":
                        continue
                    schema_section = None
                    response = None
                    try:
                        if "content" in responses_object.keys():
                            schema_section = responses_object["content"]["application/json"]["schema"]
                        elif "schema" in responses_object.keys():
                            schema_section = responses_object["schema"]
                    except KeyError:
                        pass
                    if schema_section:
                        response = response_factory(
                            schema=schema_section, url_fragment=url_fragment, method=method, status_code=status_code
                        )
                    yield schema_section, response, url_fragment


def pass_mock_value(return_value: Any) -> Any:
    def side_effect(de_parameterized_path: str, method: str):
        return return_value

    return side_effect


def mock_schema(schema) -> Callable:
    def _mocked():
        return schema

    return _mocked
