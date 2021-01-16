from openapi_tester.schema_tester import SchemaTester


def test_calls(caplog):
    """
    Make sure each type of object is passed to where it should.
    """
    SchemaTester({'type': 'array', 'items': {'type': 'object', 'properties': {}}}, [], None)
    assert 'init --> array' == caplog.records[-1].message

    SchemaTester({'type': 'object', 'properties': {}}, {}, None)
    assert 'init --> object' == caplog.records[-1].message

    SchemaTester({'type': 'string'}, '', None)
    assert 'init --> string' == caplog.records[-1].message
