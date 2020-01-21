import pytest
from openapi_tester.exceptions import SpecificationError, ImproperlyConfigured


def test_specification_error():
    with pytest.raises(SpecificationError, match='test'):
        raise SpecificationError('test')


def test_improperly_configured_error():
    with pytest.raises(ImproperlyConfigured, match='test'):
        raise ImproperlyConfigured('test')
