import glob
import os
from copy import deepcopy
from typing import Callable
from unittest.mock import patch

import pytest

from openapi_tester import (
    CaseError,
    DocumentationError,
    StaticSchemaLoader,
    UndocumentedSchemaSectionError,
    is_pascal_case,
)
from openapi_tester.schema_tester import SchemaTester
from tests.utils import CURRENT_PATH, iterate_schema, load_schema, pass_mock_value, response_factory

parameterized_path = "/api/{version}/cars/correct"
de_parameterized_path = "/api/v1/cars/correct"
method = "get"
status = "200"


def _mock_schema(schema) -> Callable:
    def _mocked():
        return schema

    return _mocked


def test_validate_response_success_scenario_with_autogenerated_data():
    static_tester = SchemaTester(schema_file_path=str(CURRENT_PATH) + "/schemas/test_project_schema.yaml")
    schema = deepcopy(load_schema("test_project_schema.yaml"))
    for schema_section, response, _ in iterate_schema(schema):
        if schema_section and response:
            static_tester.validate_response(response)
            assert sorted(static_tester.get_response_schema_section(response)) == sorted(schema_section)


def test_validate_response_success_scenario_with_predefined_data(client):
    tester = SchemaTester()
    good_test_data = [
        {
            "url": "/api/v1/cars/correct",
            "expected_response": [
                {
                    "name": "Saab",
                    "color": "Yellow",
                    "height": "Medium height",
                    "width": "Very wide",
                    "length": "2 meters",
                },
                {"name": "Volvo", "color": "Red", "height": "Medium height", "width": "Not wide", "length": "2 meters"},
                {"name": "Tesla", "color": "black", "height": "Medium height", "width": "Wide", "length": "2 meters"},
            ],
        },
        {
            "url": "/api/v1/trucks/correct",
            "expected_response": [
                {
                    "name": "Saab",
                    "color": "Yellow",
                    "height": "Medium height",
                    "width": "Very wide",
                    "length": "2 meters",
                },
                {"name": "Volvo", "color": "Red", "height": "Medium height", "width": "Not wide", "length": "2 meters"},
                {"name": "Tesla", "color": "black", "height": "Medium height", "width": "Wide", "length": "2 meters"},
            ],
        },
    ]
    for item in good_test_data:
        response = client.get(item["url"])
        assert response.status_code == 200
        assert response.json() == item["expected_response"]
        tester.validate_response(response=response)


def test_validate_response_failure_scenario_with_predefined_data(client):
    tester = SchemaTester()
    bad_test_data = [
        {
            "url": "/api/v1/cars/incorrect",
            "expected_response": [
                {"name": "Saab", "color": "Yellow", "height": "Medium height"},
                {"name": "Volvo", "color": "Red", "width": "Not very wide", "length": "2 meters"},
                {"name": "Tesla", "height": "Medium height", "width": "Medium width", "length": "2 meters"},
            ],
        },
        {
            "url": "/api/v1/trucks/incorrect",
            "expected_response": [
                {"name": "Saab", "color": "Yellow", "height": "Medium height"},
                {"name": "Volvo", "color": "Red", "width": "Not very wide", "length": "2 meters"},
                {"name": "Tesla", "height": "Medium height", "width": "Medium width", "length": "2 meters"},
            ],
        },
        {
            "url": "/api/v1/trucks/incorrect",
            "expected_response": [
                {"name": "Saab", "color": "Yellow", "height": "Medium height"},
                {"name": "Volvo", "color": "Red", "width": "Not very wide", "length": "2 meters"},
                {"name": "Tesla", "height": "Medium height", "width": "Medium width", "length": "2 meters"},
            ],
        },
    ]
    for item in bad_test_data:
        response = client.get(item["url"])
        assert response.status_code == 200
        assert response.json() == item["expected_response"]
        with pytest.raises(
            DocumentationError, match="Error: The following property is missing from the tested data: width"
        ):
            tester.validate_response(response)


def test_validate_response_failure_scenario_undocumented_path(monkeypatch):
    tester = SchemaTester()
    schema = deepcopy(tester.loader.get_schema())
    schema_section = schema["paths"][parameterized_path][method]["responses"][status]["content"]["application/json"][
        "schema"
    ]
    del schema["paths"][parameterized_path]
    monkeypatch.setattr(tester.loader, "get_schema", _mock_schema(schema))
    response = response_factory(schema_section, de_parameterized_path, method, status)
    with pytest.raises(
        UndocumentedSchemaSectionError,
        match=f"Error: Unsuccessfully tried to index the OpenAPI schema by `{parameterized_path}`.",
    ):
        tester.validate_response(response)


def test_validate_response_failure_scenario_undocumented_method(monkeypatch):
    tester = SchemaTester()
    schema = deepcopy(tester.loader.get_schema())
    schema_section = schema["paths"][parameterized_path][method]["responses"][status]["content"]["application/json"][
        "schema"
    ]
    del schema["paths"][parameterized_path][method]
    monkeypatch.setattr(tester.loader, "get_schema", _mock_schema(schema))
    response = response_factory(schema_section, de_parameterized_path, method, status)
    with pytest.raises(
        UndocumentedSchemaSectionError,
        match=f"Error: Unsuccessfully tried to index the OpenAPI schema by `{method}`.",
    ):
        tester.validate_response(response)


def test_validate_response_failure_scenario_undocumented_status_code(monkeypatch):
    tester = SchemaTester()
    schema = deepcopy(tester.loader.get_schema())
    schema_section = schema["paths"][parameterized_path][method]["responses"][status]["content"]["application/json"][
        "schema"
    ]
    del schema["paths"][parameterized_path][method]["responses"][status]
    monkeypatch.setattr(tester.loader, "get_schema", _mock_schema(schema))
    response = response_factory(schema_section, de_parameterized_path, method, status)
    with pytest.raises(
        UndocumentedSchemaSectionError,
        match=f"Error: Unsuccessfully tried to index the OpenAPI schema by `{status}`.",
    ):
        tester.validate_response(response)


def test_validate_response_global_case_tester(client):
    tester_with_case_tester = SchemaTester(case_tester=is_pascal_case)
    response = client.get(de_parameterized_path)
    with pytest.raises(CaseError, match="The response key `name` is not properly PascalCased. Expected value: Name"):
        tester_with_case_tester.validate_response(response=response)


def test_validate_response_global_ignored_case(client):
    tester_with_case_tester = SchemaTester(
        case_tester=is_pascal_case, ignore_case=["name", "color", "height", "width", "length"]
    )
    response = client.get(de_parameterized_path)
    tester_with_case_tester.validate_response(response=response)


def test_validate_response_passed_in_case_tester(client):
    tester = SchemaTester()
    response = client.get(de_parameterized_path)
    with pytest.raises(CaseError, match="The response key `name` is not properly PascalCased. Expected value: Name"):
        tester.validate_response(response=response, case_tester=is_pascal_case)


def test_validate_response_passed_in_ignored_case(client):
    tester = SchemaTester()
    response = client.get(de_parameterized_path)
    tester.validate_response(
        response=response, case_tester=is_pascal_case, ignore_case=["name", "color", "height", "width", "length"]
    )


def test_reference_schema():
    schema_path = str(CURRENT_PATH) + "/schemas"
    for schema_file in [
        f"{schema_path}/openapi_v2_reference_schema.yaml",
        f"{schema_path}/openapi_v3_reference_schema.yaml",
    ]:
        tester = SchemaTester(schema_file_path=schema_file)
        schema = tester.loader.load_schema()
        de_referenced_schema = tester.loader.de_reference_schema(schema)
        for schema_section, response, url_fragment in iterate_schema(de_referenced_schema):
            if schema_section and response:
                with patch.object(StaticSchemaLoader, "parameterize_path", side_effect=pass_mock_value(url_fragment)):
                    tester.validate_response(response)
                    # assert sorted(tester.get_response_schema_section(response)) == sorted(schema_section)  # TODO: Uncomment and fix


def test_one_of_any_of_schemas():
    tester = SchemaTester(schema_file_path=str(CURRENT_PATH) + "/schemas/one_of_any_of_test_schema.yaml")
    schema = tester.loader.load_schema()
    de_referenced_schema = tester.loader.de_reference_schema(schema)
    tester.loader.schema = de_referenced_schema
    for schema_section, response, url_fragment in iterate_schema(de_referenced_schema):
        if schema_section and response:
            with patch.object(StaticSchemaLoader, "parameterize_path", side_effect=pass_mock_value(url_fragment)):
                tester.validate_response(response)
                assert sorted(tester.get_response_schema_section(response)) == sorted(schema_section)


def test_sample_schemas():
    for filename in glob.iglob(str(CURRENT_PATH) + "/schemas/sample-schemas/**/**", recursive=True):
        if os.path.isfile(filename) and "metadata" not in filename:
            tester = SchemaTester(schema_file_path=filename)
            schema = tester.loader.load_schema()
            de_referenced_schema = tester.loader.de_reference_schema(schema)
            tester.loader.schema = de_referenced_schema
            for schema_section, response, url_fragment in iterate_schema(de_referenced_schema):
                if schema_section and response:
                    with patch.object(
                        StaticSchemaLoader, "parameterize_path", side_effect=pass_mock_value(url_fragment)
                    ):
                        tester.validate_response(response)
                        assert sorted(tester.get_response_schema_section(response)) == sorted(schema_section)
