import pytest
from django.core.exceptions import ImproperlyConfigured

from demo_project.api.serializers import ItemSerializer
from django_swagger_tester.exceptions import SwaggerDocumentationError
from django_swagger_tester.input_validation.validation import serialize_schema


def test_valid_input_validation(client):
    """
    Verifies that no exception is raised for a valid example.
    """
    from demo_project.api.swagger.auto_schemas import VehicleSerializer
    from django_swagger_tester.drf_yasg import validate_input

    validate_input(serializer=VehicleSerializer, method='POST', route='api/v1/vehicles/', camel_case_parser=True)
    validate_input(serializer=ItemSerializer, method='POST', route='api/v1/items/', camel_case_parser=True)


def test_invalid_input_validation(client):
    """
    Verifies that an appropriate exception is raised when a bad request body is passed to the validation function.
    """
    from demo_project.api.swagger.auto_schemas import VehicleSerializer
    from django_swagger_tester.drf_yasg import validate_input

    with pytest.raises(SwaggerDocumentationError, match='Request body is not valid according to the passed serializer'):
        validate_input(serializer=VehicleSerializer, method='POST', route='api/v1/vehicles/', camel_case_parser=False)


def test_serialize_schema_validation():
    """
    Make sure we raise an ImproperlyConfigured error before letting the logic fail.
    """
    with pytest.raises(
        ImproperlyConfigured, match="This schema item does not seem to have an example value. Item: {'type': 'string'}"
    ):
        serialize_schema({'type': 'string'})
