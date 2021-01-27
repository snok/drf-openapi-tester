import pytest

from openapi_tester import DocumentationError, SchemaTester

example_schema_integer = {"type": "integer", "minimum": 3, "maximum": 5}
example_integer = 3

tester = SchemaTester()


def test_nothing_wrong():
    """ This should always pass """
    tester.test_schema_section(example_schema_integer, example_integer, "")


def test_minimum_violated():
    """ Not adhering to minimum limitations should raise an error """
    with pytest.raises(
        DocumentationError,
        match="Mismatched content. Response integer violates the minimum value defined in the schema",
    ):
        tester.test_schema_section(example_schema_integer, 2, "")


def test_exactly_minimum():
    """ The minimum is included, unless specified """
    # Pass when set to minimum
    tester.test_schema_section({"type": "integer", "minimum": 3}, 3, "")
    with pytest.raises(
        DocumentationError,
        match="Mismatched content. Response integer violates the minimum value defined in the schema",
    ):
        # Fail when we exclude the minimum
        tester.test_schema_section({"type": "integer", "minimum": 3, "exclusiveMinimum": True}, 3, "")


def test_maximum_violated():
    """ Not adhering to maximum limitations should raise an error """
    with pytest.raises(
        DocumentationError,
        match="Mismatched content. Response integer violates the maximum value defined in the schema",
    ):
        tester.test_schema_section(example_schema_integer, 6, "")


def test_null():
    """ A null value should always raise an error """
    with pytest.raises(DocumentationError, match="Mismatched types, expected int but received NoneType"):
        tester.test_schema_section(example_schema_integer, None, reference="")


def test_nullable():
    """ A null value is allowed when the integer is nullable """
    schema = {"type": "integer", "nullable": True}
    tester.test_schema_section(schema, None, reference="")


def test_wrong_type():
    """ Type mismatches should raise errors """
    with pytest.raises(DocumentationError, match="expected int but received dict."):
        tester.test_schema_section(example_schema_integer, {}, "")
    with pytest.raises(DocumentationError, match="expected int but received list."):
        tester.test_schema_section(example_schema_integer, [], "")
    with pytest.raises(DocumentationError, match="expected int but received tuple."):
        tester.test_schema_section(example_schema_integer, ("test",), "")
    with pytest.raises(DocumentationError, match="expected int but received float."):
        tester.test_schema_section(example_schema_integer, 2.3, "")
