# flake8: noqa
# fmt: off
from openapi_tester.exceptions import DocumentationError
from openapi_tester.utils import format_response_tester_error

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
    expected = """Item is misspecified:\n\nSummary\n------------------------------------------------------------------------------------\n\nError:      This is a message\n\nExpected:   \n            {\n                "thisIsAVeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeryLongKey": "string"\n            }\nReceived:   \n            {\n                "thisIsAVeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeryLongKey": "test"\n            }\n\nHint:       test\nSequence:   test\n------------------------------------------------------------------------------------\n\nResponse details\n------------------------------------------------------------------------------------\ndata          {'thisIsAVeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeryLongKey': 'test'}\ntype          <class 'dict'>\n------------------------------------------------------------------------------------\n\nSchema\n------------------------------------------------------------------------------------\ntitle         object_type_title\ntype          object\nproperties    {'thisIsAVeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeryLongKey': {'description': 'This is a string type', 'type': 'string', 'example': 'string'}}\n------------------------------------------------------------------------------------\n"""
    assert format_response_tester_error(error, 'test', verbose=True) == expected

# fmt: on
