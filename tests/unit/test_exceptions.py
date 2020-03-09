import pytest
from django.core.exceptions import ImproperlyConfigured

from django_swagger_tester.exceptions import OpenAPISchemaError


def test_specification_error():
    with pytest.raises(OpenAPISchemaError, match='test'):
        raise OpenAPISchemaError('test')


def test_improperly_configured_error():
    with pytest.raises(ImproperlyConfigured, match='test'):
        raise ImproperlyConfigured('test')
