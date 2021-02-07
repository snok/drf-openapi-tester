""" Schema to Python converter """
import random
from datetime import datetime
from typing import Any, Dict, List, Optional

from openapi_tester.constants import OPENAPI_PYTHON_MAPPING
from openapi_tester.utils import combine_sub_schemas


class SchemaToPythonConverter:
    """
    This class is used both by the DocumentationError format method and the various test suites.
    """

    result: Any

    def __init__(self, schema: dict, with_faker: bool = False):
        while any(keyword in schema for keyword in ["allOf", "oneOf", "anyOf"]):
            if "allOf" in schema:
                merged_schema = combine_sub_schemas(schema["allOf"])
                schema = merged_schema
            if "anyOf" in schema:
                schema = self._handle_any_of(schema["anyOf"])
            if "oneOf" in schema:
                schema = random.sample(schema["oneOf"], 1)[0]
        if with_faker:
            # We are importing faker here to ensure this remains a dev dependency
            from faker import Faker

            Faker.seed(0)
            self.faker = Faker()
        schema_type = schema.get("type", "object")
        if schema_type == "array":
            self.result = self.convert_schema_array_to_list(schema)
        elif schema_type == "object":
            self.result = self.convert_schema_object_to_dict(schema)
        else:
            self.result = self.schema_type_to_mock_value(schema)

    @staticmethod
    def _handle_any_of(any_of_list: List[dict]) -> Dict[str, Any]:
        """ generate any of mock data """
        return combine_sub_schemas(random.sample(any_of_list, random.randint(1, len(any_of_list))))

    def schema_type_to_mock_value(self, schema_object: Dict[str, Any]) -> Any:
        schema_format: str = schema_object.get("format", "")
        schema_type: str = schema_object.get("type", "")
        enum: Optional[list] = schema_object.get("enum")
        if not hasattr(self, "faker"):
            return OPENAPI_PYTHON_MAPPING[schema_type]
        if enum:
            return enum[0]
        if schema_format and schema_type == "string":
            if schema_format == "date":
                return datetime.now().date().isoformat()
            if schema_format == "date-time":
                return datetime.now().isoformat()
            if schema_format == "byte":
                return self.faker.pystr().encode("utf-8")
        if "maximum" in schema_object or "minimum" in schema_object:
            limits = {}
            max_value = schema_object.get("maximum")
            if max_value:
                limits["max_value"] = max_value - (1 if schema_object.get("excludeMaximum") else 0)
            min_value = schema_object.get("minimum")
            if min_value:
                limits["min_value"] = min_value + (1 if schema_object.get("excludeMinimum") else 0)
            if schema_type == "integer":
                return self.faker.pyint(**limits)
            return self.faker.pyfloat(**limits)
        faker_handlers = {
            "boolean": self.faker.pybool,
            "string": self.faker.pystr,
            "file": self.faker.pystr,
            "array": self.faker.pylist,
            "object": self.faker.pydict,
            "integer": self.faker.pyint,
            "number": self.faker.pyfloat,
        }
        return faker_handlers[schema_type]()

    def convert_schema_object_to_dict(self, schema_object: dict) -> Dict[str, Any]:
        if "allOf" in schema_object:
            schema_object = combine_sub_schemas(schema_object["allOf"])
        if "oneOf" in schema_object:
            schema_object = random.sample(schema_object["oneOf"], 1)[0]
        if "anyOf" in schema_object:
            schema_object = self._handle_any_of(schema_object["anyOf"])
        if "properties" in schema_object:
            properties = schema_object["properties"]
        else:
            properties = {}

        parsed_schema: Dict[str, Any] = {}
        for key, value in properties.items():
            if "oneOf" in value:
                value = random.sample(value["oneOf"], 1)[0]
            elif "anyOf" in value:
                value = self._handle_any_of(value["anyOf"])
            value_type = value.get("type")
            if not value_type:
                if "properties" in value:
                    value_type = "object"
                elif "items" in value:
                    value_type = "array"
                else:
                    continue
            if value_type == "object":
                parsed_schema[key] = self.convert_schema_object_to_dict(value)
            elif value_type == "array":
                parsed_schema[key] = self.convert_schema_array_to_list(value)
            else:
                parsed_schema[key] = self.schema_type_to_mock_value(value)
        return parsed_schema

    def convert_schema_array_to_list(self, schema_array: Any) -> List[Any]:
        parsed_items: List[Any] = []
        raw_items = schema_array.get("items", {})
        if "allOf" in raw_items.keys():
            raw_items = combine_sub_schemas(raw_items["allOf"])
        items_type = raw_items.get("type")
        if not items_type:
            if "properties" in raw_items:
                items_type = "object"
            else:
                return []
        min_items = schema_array.get("minItems", 1)
        max_items = schema_array.get("maxItems", 1)
        while len(parsed_items) < min_items or len(parsed_items) < max_items:
            if items_type == "object":
                parsed_items.append(self.convert_schema_object_to_dict(raw_items))
            elif items_type == "array":
                parsed_items.append(self.convert_schema_array_to_list(raw_items))
            else:
                parsed_items.append(self.schema_type_to_mock_value(raw_items))
        return parsed_items
