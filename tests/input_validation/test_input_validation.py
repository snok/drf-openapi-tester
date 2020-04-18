import pytest

from django_swagger_tester.exceptions import SwaggerDocumentationError


def test_valid_input_validation(client):
    """
    Verifies that no exception is raised for a valid example.
    """
    from demo_project.api.swagger.auto_schemas import VehicleSerializer
    from django_swagger_tester.drf_yasg.base import validate_input
    validate_input(serializer=VehicleSerializer, method='POST', route='api/v1/vehicles/', camel_case_parser=True)


def test_invalid_input_validation(client):
    """
    Verifies that an appropriate exception is raised when a bad request body is passed to the validation function.
    """
    from demo_project.api.swagger.auto_schemas import VehicleSerializer
    from django_swagger_tester.drf_yasg.base import validate_input
    with pytest.raises(SwaggerDocumentationError, match='Request body is not valid according to the passed serializer'):
        validate_input(serializer=VehicleSerializer, method='POST', route='api/v1/vehicles/', camel_case_parser=False)
