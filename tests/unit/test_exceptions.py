import pytest
from openapi_tester.exceptions import OpenAPISchemaError, ImproperlyConfigured


def test_specification_error():
    with pytest.raises(OpenAPISchemaError, match='test'):
        raise OpenAPISchemaError('test')


def test_improperly_configured_error():
    with pytest.raises(ImproperlyConfigured, match='test'):
        raise ImproperlyConfigured('test')
