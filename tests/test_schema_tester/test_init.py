import pytest
from django.core.exceptions import ImproperlyConfigured

from openapi_tester.schema_tester import SchemaTester


def test_schema_tester_validation():
    """
    Make sure we're raising an error if $refs are not handled before passing the schema to the tester.
    """
    with pytest.raises(
        ImproperlyConfigured,
        match=r'Received invalid schema. You must replace \$ref sections before passing a schema for validation.',
    ):
        SchemaTester({'$ref': 'test'}, {}, lambda x, y: None, origin='test')


def test_calls(caplog):
    """
    Make sure each type of object is passed to where it should.
    """
    SchemaTester({'type': 'array', 'items': {}}, [], lambda x, y: None, origin='test')
    assert 'init --> list' == caplog.records[-1].message

    SchemaTester({'type': 'object', 'properties': {}}, {}, lambda x, y: None, origin='test')
    assert 'init --> dict' == caplog.records[-1].message

    SchemaTester({'type': 'string'}, '', lambda x, y: None, origin='test')
    assert 'init --> item' == caplog.records[-1].message
