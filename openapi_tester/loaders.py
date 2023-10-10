""" Loaders Module """
from __future__ import annotations

import difflib
import json
import pathlib
import re
from json import dumps, loads
from typing import TYPE_CHECKING, cast
from urllib.parse import urlparse

import requests
import yaml
from django.urls import Resolver404, resolve
from django.utils.functional import cached_property
from openapi_spec_validator import openapi_v2_spec_validator, openapi_v30_spec_validator, openapi_v31_spec_validator
from prance.util.resolver import RefResolver
from rest_framework.schemas.generators import BaseSchemaGenerator, EndpointEnumerator
from rest_framework.settings import api_settings

from openapi_tester.constants import UNDOCUMENTED_SCHEMA_SECTION_ERROR
from openapi_tester.exceptions import UndocumentedSchemaSectionError

if TYPE_CHECKING:
    from typing import Any, Callable
    from urllib.parse import ParseResult

    from django.urls import ResolverMatch
    from rest_framework.views import APIView


def handle_recursion_limit(schema: dict) -> Callable:
    """
    We are using a currying pattern to pass schema into the scope of the handler.
    """

    # noinspection PyUnusedLocal
    def handler(iteration: int, parse_result: ParseResult, recursions: tuple):  # pylint: disable=unused-argument
        fragment = parse_result.fragment
        keys = [key for key in fragment.split("/") if key]
        definition = schema
        for key in keys:
            definition = definition[key]
        return definition

    return handler


class BaseSchemaLoader:
    """
    Base class for OpenAPI schema loading classes.

    Contains a template of methods that are required from a loader class, and a range of helper methods for interacting
    with an OpenAPI schema.
    """

    base_path = "/"
    field_key_map: dict[str, str]
    schema: dict | None = None

    def __init__(self, field_key_map: dict[str, str] | None = None):
        super().__init__()
        self.schema: dict | None = None
        self.field_key_map = field_key_map or {}

    def load_schema(self) -> dict:
        """
        Put logic required to load a schema and return it here.
        """
        raise NotImplementedError("The `load_schema` method has to be overwritten.")

    def get_schema(self) -> dict:
        """
        Returns OpenAPI schema.
        """
        if self.schema:
            return self.schema
        self.set_schema(self.load_schema())
        return self.get_schema()

    def de_reference_schema(self, schema: dict) -> dict:
        url = schema.get("basePath", self.base_path)
        recursion_handler = handle_recursion_limit(schema)
        resolver = RefResolver(
            schema,
            recursion_limit_handler=recursion_handler,
            recursion_limit=10,
            url=url,
        )
        resolver.resolve_references()
        return resolver.specs

    def normalize_schema_paths(self, schema: dict) -> dict[str, dict]:
        normalized_paths: dict[str, dict] = {}
        for key, value in schema["paths"].items():
            try:
                parameterized_path, _ = self.resolve_path(endpoint_path=key, method=list(value.keys())[0])
                normalized_paths[parameterized_path] = value
            except ValueError:
                normalized_paths[key] = value
        return {**schema, "paths": normalized_paths}

    @staticmethod
    def validate_schema(schema: dict):
        if "openapi" in schema:
            openapi_version_pattern = re.compile(r"^(\d)\.(\d+)")
            result = openapi_version_pattern.findall(schema["openapi"])
            if result:
                major, minor = result[0]
                if (major, minor) == ("3", "0"):
                    validator = openapi_v30_spec_validator
                elif (major, minor) == ("3", "1"):
                    validator = openapi_v31_spec_validator
                else:
                    raise UndocumentedSchemaSectionError(
                        UNDOCUMENTED_SCHEMA_SECTION_ERROR.format(
                            key=schema["openapi"], error_addon="Support might need to be added."
                        )
                    )
            else:
                raise UndocumentedSchemaSectionError(UNDOCUMENTED_SCHEMA_SECTION_ERROR.format(key=schema["openapi"]))
        else:
            validator = openapi_v2_spec_validator
        validator.validate(schema)

    def set_schema(self, schema: dict) -> None:
        """
        Sets self.schema and self.original_schema.
        """
        de_referenced_schema = self.de_reference_schema(schema)
        self.validate_schema(de_referenced_schema)

        self.schema = self.normalize_schema_paths(de_referenced_schema)

    @cached_property
    def endpoints(self) -> list[str]:
        """
        Returns a list of endpoint paths.
        """
        return list({endpoint[0] for endpoint in EndpointEnumerator().get_api_endpoints()})

    def resolve_path(self, endpoint_path: str, method: str) -> tuple[str, ResolverMatch]:
        """
        Resolves a Django path.
        """
        url_object = urlparse(endpoint_path)
        parsed_path = url_object.path
        if not parsed_path.startswith("/"):
            parsed_path = "/" + parsed_path
        for key, value in self.field_key_map.items():
            if value != "pk" and key in parsed_path:
                parsed_path = parsed_path.replace(f"{{{key}}}", value)
        for path in [parsed_path, parsed_path[:-1]]:
            try:
                resolved_route = resolve(path)
            except Resolver404:
                continue
            else:
                for key, value in reversed(list(resolved_route.kwargs.items())):
                    index = path.rfind(str(value))
                    path = f"{path[:index]}{{{key}}}{path[index + len(str(value)):]}"
                if "{pk}" in path and api_settings.SCHEMA_COERCE_PATH_PK:  # noqa: FS003
                    path, resolved_route = self.handle_pk_parameter(
                        resolved_route=resolved_route, path=path, method=method
                    )
                return path, resolved_route
        message = f"Could not resolve path `{endpoint_path}`."
        close_matches = difflib.get_close_matches(endpoint_path, self.endpoints)
        if close_matches:
            message += "\n\nDid you mean one of these?\n\n- " + "\n- ".join(close_matches)
        raise ValueError(message)

    @staticmethod
    def handle_pk_parameter(resolved_route: ResolverMatch, path: str, method: str) -> tuple[str, ResolverMatch]:
        """
        Handle the DRF conversion of params called {pk} into a named parameter based on Model field
        """
        coerced_path = BaseSchemaGenerator().coerce_path(
            path=path, method=method, view=cast("APIView", resolved_route.func)
        )
        pk_field_name = "".join(
            entry.replace("+ ", "") for entry in difflib.Differ().compare(path, coerced_path) if "+ " in entry
        )
        resolved_route.kwargs[pk_field_name] = resolved_route.kwargs["pk"]
        del resolved_route.kwargs["pk"]
        return coerced_path, resolved_route


class DrfYasgSchemaLoader(BaseSchemaLoader):
    """
    Loads OpenAPI schema generated by drf_yasg.
    """

    def __init__(self, field_key_map: dict[str, str] | None = None) -> None:
        super().__init__(field_key_map=field_key_map)
        from drf_yasg.generators import OpenAPISchemaGenerator
        from drf_yasg.openapi import Info

        self.schema_generator = OpenAPISchemaGenerator(info=Info(title="", default_version=""))

    def load_schema(self) -> dict:
        """
        Loads generated schema from drf-yasg and returns it as a dict.
        """
        odict_schema = self.schema_generator.get_schema(None, True)
        return cast("dict", loads(dumps(odict_schema.as_odict())))

    def resolve_path(self, endpoint_path: str, method: str) -> tuple[str, ResolverMatch]:
        de_parameterized_path, resolved_path = super().resolve_path(endpoint_path=endpoint_path, method=method)
        path_prefix = self.schema_generator.determine_path_prefix(self.endpoints)
        trim_length = len(path_prefix) if path_prefix != "/" else 0
        return de_parameterized_path[trim_length:], resolved_path


class DrfSpectacularSchemaLoader(BaseSchemaLoader):
    """
    Loads OpenAPI schema generated by drf_spectacular.
    """

    def __init__(self, field_key_map: dict[str, str] | None = None) -> None:
        super().__init__(field_key_map=field_key_map)
        from drf_spectacular.generators import SchemaGenerator

        self.schema_generator = SchemaGenerator()

    def load_schema(self) -> dict:
        """
        Loads generated schema from drf_spectacular and returns it as a dict.
        """
        return cast("dict", loads(dumps(self.schema_generator.get_schema(public=True))))

    def resolve_path(self, endpoint_path: str, method: str) -> tuple[str, ResolverMatch]:
        from drf_spectacular.settings import spectacular_settings

        de_parameterized_path, resolved_path = super().resolve_path(endpoint_path=endpoint_path, method=method)
        return (
            de_parameterized_path[len(spectacular_settings.SCHEMA_PATH_PREFIX or "") :],
            resolved_path,
        )


class StaticSchemaLoader(BaseSchemaLoader):
    """
    Loads OpenAPI schema from a static file.
    """

    def __init__(self, path: str, field_key_map: dict[str, str] | None = None):
        super().__init__(field_key_map=field_key_map)

        self.path = path if not isinstance(path, pathlib.PosixPath) else str(path)

    def load_schema(self) -> dict[str, Any]:
        """
        Loads a static OpenAPI schema from file, and parses it to a python dict.

        :return: Schema contents as a dict
        :raises: ImproperlyConfigured
        """
        with open(self.path, encoding="utf-8") as file:
            content = file.read()
            return cast(
                "dict", json.loads(content) if ".json" in self.path else yaml.load(content, Loader=yaml.FullLoader)
            )


class UrlStaticSchemaLoader(BaseSchemaLoader):
    """
    Loads OpenAPI schema from an url static file.
    """

    def __init__(self, url: str, field_key_map: dict[str, str] | None = None):
        super().__init__(field_key_map=field_key_map)
        self.url = url

    def load_schema(self) -> dict[str, Any]:
        """
        Loads a static OpenAPI schema from url, and parses it to a python dict.

        :return: Schema contents as a dict
        :raises: ImproperlyConfigured
        """
        response = requests.get(self.url, timeout=20)
        return cast(
            "dict",
            (
                json.loads(response.content)
                if ".json" in self.url
                else yaml.load(response.content, Loader=yaml.FullLoader)
            ),
        )
