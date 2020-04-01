import pytest

from django_swagger_tester.exceptions import SwaggerDocumentationError
from django_swagger_tester.response_validation.base.base import SwaggerTestBase
from tests.unit.base.test_unpack_response import MockResponse

base = SwaggerTestBase()
response = MockResponse()
response.status_code = 200


def test_validate_response_raises():
    """
    Make sure we're raising an error hwen self.schema doesn't get defined by load_schema.
    """
    with pytest.raises(SwaggerDocumentationError, match='The OpenAPI schema is undefined. Schema is not testable.'):
        base._validate_response(response=response, method='GET', endpoint_url='api/v1/cars/correct')


def test_validate_response_calls_dict():
    """
    Make sure we're calling the right base methods.
    """

    def raise_exc(*args, **kwargs):
        raise Exception('called')

    base._dict = raise_exc
    base.schema = {'type': 'object'}
    with pytest.raises(Exception, match='called'):
        base._validate_response(response=response, method='GET', endpoint_url='api/v1/cars/correct')


def test_validate_response_calls_list():
    """
    Make sure we're calling the right base methods.
    """

    def raise_exc(*args, **kwargs):
        raise Exception('called')

    base._list = raise_exc
    base.schema = {'type': 'array'}
    with pytest.raises(Exception, match='called'):
        base._validate_response(response=response, method='GET', endpoint_url='api/v1/cars/correct')


def test_validate_response_calls_item():
    """
    Make sure we're calling the right base methods.
    """

    def raise_exc(*args, **kwargs):
        raise Exception('called')

    base._item = raise_exc
    for schema_type in ['string', 'boolean', 'number', 'integer']:
        base.schema = {'type': schema_type}
        with pytest.raises(Exception, match='called'):
            base._validate_response(response=response, method='GET', endpoint_url='api/v1/cars/correct')


def test_exception():
    """
    Make sure we're raising an exception for a bad schema type.
    """
    base.schema = {'type': 'bad_type'}
    with pytest.raises(Exception,
                       match="Unexpected error.\nSchema: {'type': 'bad_type'}\nResponse: {'test': 'test'}\n\nThis shouldn't happen"):
        base._validate_response(response=response, method='GET', endpoint_url='api/v1/cars/correct')
