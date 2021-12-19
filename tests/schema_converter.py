""" Schema to Python converter """
import base64
import random
from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from faker import Faker

from openapi_tester.utils import merge_objects, normalize_schema_section


class SchemaToPythonConverter:
    """
    This class is used by various test suites.
    """

    result: Any
    faker: Faker = Faker()

    def __init__(self, schema: dict):
        Faker.seed(0)
        self.faker = Faker()
        self.result = self.convert_schema(deepcopy(schema))

    def convert_schema(self, schema: Dict[str, Any]) -> Any:
        schema_type = schema.get("type", "object")
        schema = normalize_schema_section(schema)
        if "oneOf" in schema:
            one_of = schema.pop("oneOf")
            return self.convert_schema({**schema, **random.sample(one_of, 1)[0]})
        if "anyOf" in schema:
            any_of = schema.pop("anyOf")
            return self.convert_schema(
                {**schema, **merge_objects(random.sample(any_of, random.randint(1, len(any_of))))}
            )
        if schema_type == "array":
            return self.convert_schema_array_to_list(schema)
        if schema_type == "object":
            return self.convert_schema_object_to_dict(schema)
        return self.schema_type_to_mock_value(schema)

    def schema_type_to_mock_value(self, schema_object: Dict[str, Any]) -> Any:
        faker_handler_map = {
            # by type
            "array": self.faker.pylist,
            "boolean": self.faker.pybool,
            "file": self.faker.pystr,
            "integer": self.faker.pyint,
            "number": self.faker.pyfloat,
            "object": self.faker.pydict,
            "string": self.faker.pystr,
            # by format
            "byte": lambda: base64.b64encode(self.faker.pystr().encode("utf-8")).decode("utf-8"),
            "date": lambda: datetime.now().date().isoformat(),
            "date-time": lambda: datetime.now().isoformat(),
            "double": self.faker.pyfloat,
            "email": self.faker.email,
            "float": self.faker.pyfloat,
            "ipv4": self.faker.ipv4,
            "ipv6": self.faker.ipv6,
            "time": self.faker.time,
            "uri": self.faker.uri,
            "url": self.faker.url,
            "uuid": self.faker.uuid4,
        }
        schema_format: str = schema_object.get("format", "")
        schema_type: str = schema_object.get("type", "")
        minimum: Optional[Union[int, float]] = schema_object.get("minimum")
        maximum: Optional[Union[int, float]] = schema_object.get("maximum")
        enum: Optional[list] = schema_object.get("enum")
        if enum:
            return random.sample(enum, 1)[0]
        if schema_type in ["integer", "number"] and (minimum is not None or maximum is not None):
            if minimum is not None:
                minimum += 1 if schema_object.get("exclusiveMinimum") else 0
            if maximum is not None:
                maximum -= 1 if schema_object.get("exclusiveMaximum") else 0
            if minimum is not None or maximum is not None:  # pragma: no cover
                minimum = minimum or 0
                maximum = maximum or minimum * 2
                if schema_type == "integer":
                    return self.faker.pyint(minimum, maximum)
                return random.uniform(minimum, maximum)
        return (
            faker_handler_map[schema_format]()
            if schema_format in faker_handler_map
            else faker_handler_map[schema_type]()
        )

    def convert_schema_object_to_dict(self, schema_object: dict) -> Dict[str, Any]:
        properties = schema_object.get("properties", {})
        parsed_schema: Dict[str, Any] = {}
        for key, value in properties.items():
            parsed_schema[key] = self.convert_schema(value)
        return parsed_schema

    def convert_schema_array_to_list(self, schema_array: Any) -> List[Any]:
        parsed_items: List[Any] = []
        items = self.convert_schema(schema_array.get("items", {}))
        min_items = schema_array.get("minItems", 1)
        max_items = schema_array.get("maxItems", 1)
        while len(parsed_items) < min_items or len(parsed_items) < max_items:
            parsed_items.append(items)
        return parsed_items
