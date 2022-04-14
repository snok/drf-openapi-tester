import json

import pytest
from rest_framework import status

from openapi_tester.clients import OpenAPIClient
from openapi_tester.exceptions import UndocumentedSchemaSectionError
from openapi_tester.schema_tester import SchemaTester


@pytest.fixture()
def openapi_client(settings) -> OpenAPIClient:
    """Sample ``OpenAPIClient`` instance to use in tests."""
    # use `drf-yasg` schema loader in tests
    settings.INSTALLED_APPS = [app for app in settings.INSTALLED_APPS if app != "drf_spectacular"]
    return OpenAPIClient(schema_tester=SchemaTester())


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
