from openapi_tester.exceptions import DocumentationError

error = DocumentationError(
    message='This is a message',
    response={'thisIsAVeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeryLongKey': 'test'},
    schema={
        'title': 'object_type_title',
        'type': 'object',
        'properties': {
            'thisIsAVeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeryLongKey': {
                'description': 'This is a string type',
                'type': 'string',
                'example': 'string',
            }
        },
    },
    reference='test',
    hint='test',
)


def test_format():
    expected = """Item is misspecified:

Summary
------------------------------------------------------------------------------------

Error:      This is a message

Expected:   {'thisIsAVeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeryLongKey': 'string'}
Received:   {'thisIsAVeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeryLongKey': 'test'}

Hint:       test
Sequence:   test

------------------------------------------------------------------------------------

* If you need more details: set `verbose=True`"""
    assert error.format() == expected
