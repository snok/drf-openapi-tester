import pytest

from openapi_tester import DocumentationError
from openapi_tester.constants import ANY_OF_ERROR, ONE_OF_ERROR
from tests.schema_tester_tests import docs_anyof_example, example_anyof_response, tester


def test_any_of():
    # Test first possibility
    tester.test_schema_section(example_anyof_response, {"oneKey": "test"})

    # Test second possibility
    tester.test_schema_section(example_anyof_response, {"anotherKey": 1})

    # Test a few bad responses
    data = [
        {"oneKey": 1},  # bad type
        {"anotherKey": "test"},  # bad type
        {"thirdKey": "test"},  # bad key
        {"thirdKey": 1},  # bad key
        [],  # bad type
        "test",  # bad type
        1,  # bad type
    ]
    for datum in data:
        with pytest.raises(DocumentationError, match=ANY_OF_ERROR):
            tester.test_schema_section(example_anyof_response, datum)


def test_any_of_official_documentation_example():
    """
    This test makes sure our anyOf implementation works as described in the official example docs:
    https://swagger.io/docs/specification/data-models/oneof-anyof-allof-not/#anyof
    """
    tester.test_schema_section(docs_anyof_example, {"age": 50})
    tester.test_schema_section(docs_anyof_example, {"pet_type": "Cat", "hunts": True})
    tester.test_schema_section(docs_anyof_example, {"nickname": "Fido", "pet_type": "Dog", "age": 44})

    with pytest.raises(DocumentationError):
        tester.test_schema_section(docs_anyof_example, {"nickname": "Mr. Paws", "hunts": False})


def test_one_of():
    all_types = [
        {"type": "string"},
        {"type": "number"},
        {"type": "integer"},
        {"type": "boolean"},
        {"type": "array", "items": {}},
        {"type": "object"},
    ]

    # Make sure integers are validated correctly
    non_int_types = all_types[:1] + all_types[3:]
    int_types = all_types[1:3]
    int_value = 1
    for type in non_int_types:
        with pytest.raises(DocumentationError, match=ONE_OF_ERROR.format(matches=0)):
            tester.test_schema_section({"oneOf": [type]}, int_value)
    for type in int_types:
        tester.test_schema_section({"oneOf": [type]}, int_value)

    # Make sure strings are validated correctly
    non_string_types = all_types[1:]
    string_types = all_types[:1]
    string_value = "test"
    for type in non_string_types:
        with pytest.raises(DocumentationError, match=ONE_OF_ERROR.format(matches=0)):
            tester.test_schema_section({"oneOf": [type]}, string_value)
    for type in string_types:
        tester.test_schema_section({"oneOf": [type]}, string_value)

    # Make sure booleans are validated correctly
    non_boolean_types = all_types[:3] + all_types[4:]
    boolean_types = [all_types[3]]
    boolean_value = False
    for type in non_boolean_types:
        with pytest.raises(DocumentationError, match=ONE_OF_ERROR.format(matches=0)):
            tester.test_schema_section({"oneOf": [type]}, boolean_value)
    for type in boolean_types:
        tester.test_schema_section({"oneOf": [type]}, boolean_value)

    # Make sure arrays are validated correctly
    non_array_types = all_types[:4] + all_types[5:]
    array_types = [all_types[4]]
    array_value = []
    for type in non_array_types:
        with pytest.raises(DocumentationError, match=ONE_OF_ERROR.format(matches=0)):
            tester.test_schema_section({"oneOf": [type]}, array_value)
    for type in array_types:
        tester.test_schema_section({"oneOf": [type]}, array_value)

    # Make sure arrays are validated correctly
    non_object_types = all_types[:5]
    object_types = [all_types[5]]
    object_value = {}
    for type in non_object_types:
        with pytest.raises(DocumentationError, match=ONE_OF_ERROR.format(matches=0)):
            tester.test_schema_section({"oneOf": [type]}, object_value)
    for type in object_types:
        tester.test_schema_section({"oneOf": [type]}, object_value)

    # Make sure we raise the appropriate error when we find several matches
    with pytest.raises(DocumentationError, match=ONE_OF_ERROR.format(matches=2)):
        tester.test_schema_section(
            {
                "oneOf": [
                    {"type": "string"},
                    {"type": "number"},
                    {"type": "integer"},
                    {"type": "boolean"},
                    {"type": "array", "items": {}},
                    {"type": "object"},
                ]
            },
            1,
        )

    # Make sure we raise the appropriate error when we find no matches
    with pytest.raises(DocumentationError, match=ONE_OF_ERROR.format(matches=0)):
        tester.test_schema_section(
            {
                "oneOf": [
                    {"type": "number"},
                    {"type": "integer"},
                    {"type": "boolean"},
                    {"type": "array", "items": {}},
                    {"type": "object"},
                ]
            },
            "test",
        )
