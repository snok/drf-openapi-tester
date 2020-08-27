import pytest

from demo.api.serializers import ItemSerializer
from django_swagger_tester.exceptions import SwaggerDocumentationError


def test_valid_input_validation(client):
    """
    Verifies that no exception is raised for a valid example.
    """
    from demo.api.swagger.auto_schemas import VehicleSerializer
    from django_swagger_tester.testing import validate_input_serializer

    validate_input_serializer(
        serializer=VehicleSerializer, method='POST', route='api/v1/vehicles/', camel_case_parser=True
    )
    validate_input_serializer(serializer=ItemSerializer, method='POST', route='api/v1/items/', camel_case_parser=True)


def test_invalid_input_validation(client):
    """
    Verifies that an appropriate exception is raised when a bad request body is passed to the validation function.
    """
    from demo.api.swagger.auto_schemas import VehicleSerializer
    from django_swagger_tester.testing import validate_input_serializer

    with pytest.raises(SwaggerDocumentationError, match='Request body is not valid according to the passed serializer'):
        validate_input_serializer(
            serializer=VehicleSerializer, method='POST', route='api/v1/vehicles/', camel_case_parser=False
        )
