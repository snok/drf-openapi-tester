import pytest

from openapi_tester import OpenAPISchemaError, SchemaTester

example_schema_array = {"type": "array", "items": {"type": "string"}}
example_array = ["string"]

tester = SchemaTester()


def test_bad_schema_type():
    """
    Unsupported schema types should raise an error.
    """
    for _type in ["str", "list", "dict", "123", 123]:
        with pytest.raises(OpenAPISchemaError, match="Received bad schema type: str"):
            schema_array = {"type": "array", "items": {"type": _type}}
            tester.test_schema_section(schema_array, example_array, reference="")
