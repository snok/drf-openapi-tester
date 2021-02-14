import glob
import os
from copy import deepcopy
from unittest.mock import patch

import pytest

from openapi_tester import (
    CaseError,
    DocumentationError,
    SchemaTester,
    StaticSchemaLoader,
    UndocumentedSchemaSectionError,
    is_pascal_case,
)
from tests.schema_tester_tests import bad_test_data, de_parameterized_path, method, parameterized_path, status, tester
from tests.utils import CURRENT_PATH, _mock_schema, iterate_schema, pass_mock_value, response_factory


@pytest.mark.parametrize(
    "filename",
    [
        filename
        for filename in glob.iglob(str(CURRENT_PATH) + "/schemas/**/**", recursive=True)
        if os.path.isfile(filename) and "metadata" not in filename
    ],
)
def test_example_schemas(filename):
    """
    This is an automated integration test template, for each schema in the "../schemas" folder a test is generated
    """
    schema_tester = SchemaTester(schema_file_path=filename)
    schema = schema_tester.loader.load_schema()
    de_referenced_schema = schema_tester.loader.de_reference_schema(schema)
    schema_tester.loader.schema = de_referenced_schema
    for schema_section, response, url_fragment in iterate_schema(de_referenced_schema):
        if schema_section and response:
            with patch.object(StaticSchemaLoader, "parameterize_path", side_effect=pass_mock_value(url_fragment)):
                schema_tester.validate_response(response)
                assert sorted(schema_tester.get_response_schema_section(response)) == sorted(schema_section)


def test_validate_response_failure_scenario_with_predefined_data(client):
    for item in bad_test_data:
        response = client.get(item["url"])
        assert response.status_code == 200
        assert response.json() == item["expected_response"]
        with pytest.raises(DocumentationError, match="The following property is missing from the tested data: width"):
            tester.validate_response(response)


def test_validate_response_failure_scenario_undocumented_path(monkeypatch):
    schema = deepcopy(tester.loader.get_schema())
    schema_section = schema["paths"][parameterized_path][method]["responses"][status]["content"]["application/json"][
        "schema"
    ]
    del schema["paths"][parameterized_path]
    monkeypatch.setattr(tester.loader, "get_schema", _mock_schema(schema))
    response = response_factory(schema_section, de_parameterized_path, method, status)
    with pytest.raises(
        UndocumentedSchemaSectionError,
        match=f"Unsuccessfully tried to index the OpenAPI schema by `{parameterized_path}`.",
    ):
        tester.validate_response(response)


def test_validate_response_failure_scenario_undocumented_method(monkeypatch):
    schema = deepcopy(tester.loader.get_schema())
    schema_section = schema["paths"][parameterized_path][method]["responses"][status]["content"]["application/json"][
        "schema"
    ]
    del schema["paths"][parameterized_path][method]
    monkeypatch.setattr(tester.loader, "get_schema", _mock_schema(schema))
    response = response_factory(schema_section, de_parameterized_path, method, status)
    with pytest.raises(
        UndocumentedSchemaSectionError,
        match=f"Unsuccessfully tried to index the OpenAPI schema by `{method}`.",
    ):
        tester.validate_response(response)


def test_validate_response_failure_scenario_undocumented_status_code(monkeypatch):
    schema = deepcopy(tester.loader.get_schema())
    schema_section = schema["paths"][parameterized_path][method]["responses"][status]["content"]["application/json"][
        "schema"
    ]
    del schema["paths"][parameterized_path][method]["responses"][status]
    monkeypatch.setattr(tester.loader, "get_schema", _mock_schema(schema))
    response = response_factory(schema_section, de_parameterized_path, method, status)
    with pytest.raises(
        UndocumentedSchemaSectionError,
        match=f"Unsuccessfully tried to index the OpenAPI schema by `{status}`.",
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
    response = client.get(de_parameterized_path)
    with pytest.raises(CaseError, match="The response key `name` is not properly PascalCased. Expected value: Name"):
        tester.validate_response(response=response, case_tester=is_pascal_case)


def test_validate_response_passed_in_ignored_case(client):
    response = client.get(de_parameterized_path)
    tester.validate_response(
        response=response, case_tester=is_pascal_case, ignore_case=["name", "color", "height", "width", "length"]
    )
