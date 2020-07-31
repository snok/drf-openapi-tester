import pytest
from django.core.exceptions import ImproperlyConfigured

from django_swagger_tester.schema_validation.response.base import ResponseTester


def test_validation():
    """
    Make sure we're raising an error if $refs are not handled before passing the schema to the tester.
    """
    with pytest.raises(
        ImproperlyConfigured,
        match='Received invalid schema. You must replace \$ref sections before passing a schema for validation.',
    ):
        ResponseTester({'$ref': 'test'}, {})


def test_calls(caplog):
    """
    Make sure each type of object is passed to where it should.
    """
    ResponseTester({'type': 'array', 'items': {}}, [])
    assert 'init --> list' == caplog.records[-1].message

    ResponseTester({'type': 'object', 'properties': {}}, {})
    assert 'init --> dict' == caplog.records[-1].message

    ResponseTester({'type': 'string'}, '')
    assert 'init --> item' == caplog.records[-1].message
