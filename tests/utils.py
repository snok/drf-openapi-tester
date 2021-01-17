import json
from pathlib import Path

import yaml
from rest_framework.response import Response

from openapi_tester.schema_converter import SchemaToPythonConverter

CURRENT_PATH = Path(__file__).resolve(strict=True).parent


def load_schema(file_name: str) -> dict:
    with open(str(CURRENT_PATH) + f'/schemas/{file_name}') as f:
        content = f.read()
        if 'json' in file_name:
            return json.loads(content)
        else:
            return yaml.load(content, Loader=yaml.FullLoader)


def response_factory(schema: dict, path: str, method: str, status_code: int = 200) -> Response:
    converted_schema = SchemaToPythonConverter(schema, with_faker=True)
    response = Response(status=status_code, data=converted_schema)
    response.request = dict(REQUEST_METHOD=method, PATH_INFO=path)
    return response
