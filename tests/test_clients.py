import functools
import json

import pytest
from django.test.testcases import SimpleTestCase
from rest_framework import status

from openapi_tester.clients import OpenAPIClient
from openapi_tester.exceptions import UndocumentedSchemaSectionError
from openapi_tester.schema_tester import SchemaTester


@pytest.fixture()
def openapi_client(settings) -> OpenAPIClient:
    """Sample ``OpenAPIClient`` instance to use in tests."""
    # use `drf-yasg` schema loader in tests
    settings.INSTALLED_APPS = [app for app in settings.INSTALLED_APPS if app != "drf_spectacular"]
    return OpenAPIClient()


def test_init_schema_tester_passed():
    """Ensure passed ``SchemaTester`` instance is used."""
    schema_tester = SchemaTester()

    client = OpenAPIClient(schema_tester=schema_tester)

    assert client.schema_tester is schema_tester


@pytest.mark.parametrize(
    ("generic_kwargs", "expected_status_code"),
    [
        (
            {"method": "GET", "path": "/api/v1/cars/correct"},
            status.HTTP_200_OK,
        ),
        (
            {
                "method": "POST",
                "path": "/api/v1/vehicles",
                "data": json.dumps({"vehicle_type": "suv"}),
                "content_type": "application/json",
            },
            status.HTTP_201_CREATED,
        ),
    ],
)
def test_request(openapi_client, generic_kwargs, expected_status_code):
    """Ensure ``SchemaTester`` doesn't raise exception when response valid."""
    response = openapi_client.generic(**generic_kwargs)

    assert response.status_code == expected_status_code


def test_request_on_empty_list(openapi_client):
    """Ensure ``SchemaTester`` doesn't raise exception when response is empty list."""
    response = openapi_client.generic(
        method="GET",
        path="/api/v1/empty-names",
        content_type="application/json",
    )
    assert response.status_code == status.HTTP_200_OK, response.data


@pytest.mark.parametrize(
    ("generic_kwargs", "raises_kwargs"),
    [
        (
            {
                "method": "POST",
                "path": "/api/v1/vehicles",
                "data": json.dumps({"vehicle_type": ("1" * 50)}),
                "content_type": "application/json",
            },
            {
                "expected_exception": UndocumentedSchemaSectionError,
                "match": "Undocumented status code: 400",
            },
        ),
        (
            {"method": "PUT", "path": "/api/v1/animals"},
            {
                "expected_exception": UndocumentedSchemaSectionError,
                "match": "Undocumented method: put",
            },
        ),
    ],
)
def test_request_invalid_response(
    openapi_client,
    generic_kwargs,
    raises_kwargs,
):
    """Ensure ``SchemaTester`` raises an exception when response is invalid."""
    with pytest.raises(**raises_kwargs):  # noqa: PT010
        openapi_client.generic(**generic_kwargs)


@pytest.mark.parametrize(
    "openapi_client_class",
    [
        OpenAPIClient,
        functools.partial(OpenAPIClient, schema_tester=SchemaTester()),
    ],
)
def test_django_testcase_client_class(openapi_client_class):
    """Ensure example from README.md about Django test case works fine."""

    class DummyTestCase(SimpleTestCase):
        """Django ``TestCase`` with ``OpenAPIClient`` client."""

        client_class = openapi_client_class

    test_case = DummyTestCase()
    test_case._pre_setup()

    assert isinstance(test_case.client, OpenAPIClient)
