import pytest

from django_swagger_tester.exceptions import SwaggerDocumentationError
from django_swagger_tester.response_validation.drf_yasg import DrfYasgSwaggerTester, validate_response



def test_endpoints_dynamic_schema(client) -> None:  # noqa: TYP001
    """
    Asserts that the validate_response function validates correct schemas successfully.
    """
    response = client.post('/api/v1/vehicles/', headers={'Content-Type':'application/json'}, data={'vehicleType': 'truck'})
    validate_response(response=response, method='POST', endpoint_url='api/v1/vehicles')
