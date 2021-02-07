import random
from datetime import datetime
from typing import Any, Dict, List

from openapi_tester.constants import OPENAPI_PYTHON_MAPPING


class SchemaToPythonConverter:
    """
    This class is used both by the DocumentationError format method and the various test suites.
    """

    def __init__(self, schema: dict, with_faker: bool = False):
        while any(keyword in schema for keyword in ["allOf", "oneOf", "anyOf"]):
            if "allOf" in schema:
                from openapi_tester.schema_tester import SchemaTester

                merged_schema = SchemaTester.combine_sub_schemas(schema["allOf"])
                schema = merged_schema
            if "oneOf" in schema:
                schema = random.sample(schema["oneOf"], 1)[0]
            if "anyOf" in schema:
                schema = self._handle_any_of(schema["anyOf"])
        if with_faker:
            # We are importing faker here to ensure this remains a dev dependency
            from faker import Faker

            Faker.seed(0)
            self.faker = Faker()
        schema_type = schema.get("type", "object")
        if schema_type == "array":
            self.result = self._iterate_schema_list(schema)  # type :ignore
        elif schema_type == "object":
            self.result = self._iterate_schema_dict(schema)  # type :ignore
        else:
            self.result = self._to_mock_value(schema)  # type :ignore

    def _to_mock_value(self, schema_object) -> Any:
        schema_format = schema_object.get("format")
        schema_type = schema_object.get("type")
        enum = schema_object.get("enum")
        if not hasattr(self, "faker"):
            return OPENAPI_PYTHON_MAPPING[schema_type]

        if enum:
            return enum[0]
        elif schema_format:
            if schema_type == "string":
                if schema_format == "date":
                    return datetime.now().date().isoformat()
                elif schema_format == "date-time":
                    return datetime.now().isoformat()
                elif schema_format == "byte":
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
            else:
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

    def _handle_any_of(self, any_of_list: List[dict]) -> Dict[str, Any]:
        """ generate any of mock data """
        from openapi_tester.schema_tester import SchemaTester

        return SchemaTester.combine_sub_schemas(random.sample(any_of_list, random.randint(1, len(any_of_list))))

    def _iterate_schema_dict(self, schema_object: dict) -> Any:
        parsed_schema = {}
        if "allOf" in schema_object:
            from openapi_tester.schema_tester import SchemaTester

            schema_object = SchemaTester.combine_sub_schemas(schema_object["allOf"])
        if "anyOf" in schema_object:
            schema_object = self._handle_any_of(schema_object["anyOf"])
        if "oneOf" in schema_object:
            schema_object = random.sample(schema_object["oneOf"], 1)[0]
        if "properties" in schema_object:
            properties = schema_object["properties"]
        else:
            properties = {}

        for key, value in properties.items():
            if "example" in value:
                parsed_schema[key] = value["example"]
            elif "anyOf" in value:
                value = self._iterate_schema_dict(self._handle_any_of(value["anyOf"]))
            elif "oneOf" in value:
                value = random.sample(value["oneOf"], 1)[0]
            value_type = value.get("type")
            if not value_type and "properties" in value:
                value_type = "object"
            elif not value_type:
                continue
            if value_type == "object":
                parsed_schema[key] = self._iterate_schema_dict(value)
            elif value_type == "array":
                parsed_schema[key] = self._iterate_schema_list(value)
            else:
                parsed_schema[key] = self._to_mock_value(value)
        return parsed_schema

    def _iterate_schema_list(self, schema_array: Any) -> List[Any]:
        parsed_items: List[Any] = []
        raw_items = schema_array.get("items", {})
        if "allOf" in raw_items.keys():
            from openapi_tester.schema_tester import SchemaTester

            raw_items = SchemaTester.combine_sub_schemas(raw_items["allOf"])
        items_type = raw_items.get("type")
        if not items_type:
            if "properties" in raw_items:
                items_type = "object"
            else:
                return []
        if items_type == "object":
            parsed_items.append(self._iterate_schema_dict(raw_items))
        elif items_type == "array":
            parsed_items.append(self._iterate_schema_list(raw_items))
        else:
            parsed_items.append(self._to_mock_value(raw_items))
        return parsed_items
