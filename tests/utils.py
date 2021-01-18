import json
import re
from pathlib import Path
from typing import Optional, Tuple

import yaml
from django.urls import path
from django.urls.resolvers import RoutePattern
from rest_framework.response import Response
from rest_framework.views import APIView

from openapi_tester.constants import PARAMETER_CAPTURE_REGEX
from openapi_tester.schema_converter import SchemaToPythonConverter

CURRENT_PATH = Path(__file__).resolve(strict=True).parent


def load_schema(file_name: str) -> dict:
    with open(str(CURRENT_PATH) + f'/schemas/{file_name}') as f:
        content = f.read()
        if 'json' in file_name:
            return json.loads(content)
        else:
            return yaml.load(content, Loader=yaml.FullLoader)


def response_factory(schema: dict, url_fragment: str, method: str, status_code: int = 200) -> Response:
    converted_schema = SchemaToPythonConverter(schema, with_faker=True).result
    response = Response(status=status_code, data=converted_schema)
    response.request = dict(REQUEST_METHOD=method, PATH_INFO=url_fragment)
    response.json = lambda: converted_schema
    return response


def url_pattern_factory(schema: dict) -> Tuple[str, RoutePattern]:
    for url_fragment, path_object in schema['paths'].items():
        for parameter in list(re.findall(PARAMETER_CAPTURE_REGEX, url_fragment)):
            parameter_name = parameter.replace('{', '').replace('}', '')
            url_fragment = url_fragment.replace(parameter, f'<{parameter_name}:str>')
        yield url_fragment, path(url_fragment, APIView.as_view())


def iterate_schema(schema: dict) -> Tuple[Optional[dict], Optional[Response]]:
    for url_fragment, path_object in schema['paths'].items():
        for method, method_object in path_object.items():
            for status_code, responses_object in method_object['responses'].items():
                if status_code == 'default':
                    # TODO: Handle this
                    # Added this temporarily for schema v2 reference l62
                    continue
                schema_section = None
                response = None
                if 'content' in responses_object.keys():
                    schema_section = responses_object['content']['application/json']['schema']
                elif 'schema' in responses_object.keys():
                    schema_section = responses_object['schema']
                if schema_section:
                    response = response_factory(
                        schema=schema_section, url_fragment=url_fragment, method=method, status_code=status_code
                    )
                yield schema_section, response, url_fragment
