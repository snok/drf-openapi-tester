import pytest

from openapi_tester import DocumentationError, SchemaTester

example_schema_number = {"type": "number", "minimum": 3, "maximum": 5}
example_number = 3.2

tester = SchemaTester()


# region: number


def test_nothing_wrong():
    """ This should always pass """
    tester.test_schema_section(example_schema_number, example_number)


def test_minimum_violated():
    """ Not adhering to minimum limitations should raise an error """
    with pytest.raises(
        DocumentationError,
        match="Mismatched content. Response number violates the minimum value defined in the schema",
    ):
        tester.test_schema_section(example_schema_number, 2)


def test_exclusives():
    """ The minimum is included, unless specified """

    # Pass when set to minimum
    schema = {"type": "number", "minimum": 3, "exclusiveMinimum": False}
    tester.test_schema_section(schema, 3)

    # Fail when we exclude the minimum
    schema["exclusiveMinimum"] = True
    with pytest.raises(
        DocumentationError,
        match="Mismatched content. Response integer violates the minimum value defined in the schema",
    ):
        tester.test_schema_section(schema, 3)

    # Fail when we exclude the maximum
    schema["exlusiveMaximum"] = True
    with pytest.raises(
        DocumentationError,
        match="Mismatched content. Response integer violates the minimum value defined in the schema",
    ):
        tester.test_schema_section(schema, 5)

    # Pass when we include the maximum
    schema["exlusiveMaximum"] = False
    tester.test_schema_section(schema, 5)


def test_maximum_violated():
    """ Not adhering to maximum limitations should raise an error """
    with pytest.raises(
        DocumentationError, match="Mismatched content. Response number violates the maximum value defined in the schema"
    ):
        tester.test_schema_section(example_schema_number, 6)


def test_null():
    """ A null value should always raise an error """
    with pytest.raises(DocumentationError, match="Mismatched types, expected int or float but received NoneType"):
        tester.test_schema_section(example_schema_number, None, reference="")


def test_nullable():
    """ A null value is allowed when the number is nullable """
    schema = {"type": "number", "nullable": True}
    tester.test_schema_section(schema, None, reference="")


def test_wrong_type():
    """ Type mismatches should raise errors """
    with pytest.raises(DocumentationError, match="expected int or float but received dict."):
        tester.test_schema_section(example_schema_number, {})
    with pytest.raises(DocumentationError, match="expected int or float but received list."):
        tester.test_schema_section(example_schema_number, [])
    with pytest.raises(DocumentationError, match="expected int or float but received tuple."):
        tester.test_schema_section(example_schema_number, ("test",))


def test_multiple_of():
    # Pass
    schema = {"multipleOf": 5, "type": "number"}
    for number in [5, 10, 15, 20, 25]:
        tester.test_schema_section(schema, number)

    # Fail
    with pytest.raises(DocumentationError, match="The response number must be a multiple of 5, but is 7."):
        tester.test_schema_section(schema, 7)


# endregion: number

# region: special formats

# TODO: float format tests
# TODO: double format tests

# endregion: special formats
