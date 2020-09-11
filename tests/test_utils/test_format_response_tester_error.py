from django_swagger_tester.exceptions import SwaggerDocumentationError
from django_swagger_tester.utils import format_response_tester_error

error = SwaggerDocumentationError(
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
    response_hint='test',
    request_hint='test',
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
    assert format_response_tester_error(error, 'test') == expected


def test_verbose_format():
    expected = """Item is misspecified:

Summary
------------------------------------------------------------------------------------

Error:      This is a message

Expected:
            {
                "thisIsAVeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeryLongKey": "string"
            }
Received:
            {
                "thisIsAVeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeryLongKey": "test"
            }

Hint:       test
Sequence:   test
------------------------------------------------------------------------------------

Response details
------------------------------------------------------------------------------------
data          {'thisIsAVeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeryLongKey': 'test'}
type          <class 'dict'>
------------------------------------------------------------------------------------

Schema
------------------------------------------------------------------------------------
title         object_type_title
type          object
properties    {'thisIsAVeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeryLongKey': {'description': 'This is a string type', 'type': 'string', 'example': 'string'}}
------------------------------------------------------------------------------------
"""
    assert format_response_tester_error(error, 'test', verbose=True) == expected
