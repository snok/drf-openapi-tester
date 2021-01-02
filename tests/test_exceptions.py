import pytest
from django.core.exceptions import ImproperlyConfigured

from response_tester.exceptions import DocumentationError


def test_specification_error():
    with pytest.raises(DocumentationError, match='test'):
        raise DocumentationError('test')


def test_improperly_configured_error():
    with pytest.raises(ImproperlyConfigured, match='test'):
        raise ImproperlyConfigured('test')
