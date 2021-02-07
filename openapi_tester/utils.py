""" Utils Module - this file contains utility functions used in multiple places """
from typing import Any, Dict, List


def combine_object_schemas(schemas: List[dict]) -> Dict[str, Any]:
    properties: Dict[str, Any] = {}
    required = []
    for entry in schemas:
        required.extend(entry.get("required", []))
        for key, value in entry.get("properties", {}).items():
            if key in properties and isinstance(value, dict):
                properties[key] = {**properties[key], **value}
            elif key in properties and isinstance(value, list):
                properties[key] = [*properties[key], *value]
            else:
                properties[key] = value
    return {"type": "object", "required": required, "properties": properties}


def combine_sub_schemas(schemas: List[dict]) -> Dict[str, Any]:
    array_schemas = [schema for schema in schemas if schema.get("type") == "array"]
    if array_schemas:
        return {
            "type": "array",
            "items": combine_object_schemas([schema.get("items", {}) for schema in array_schemas]),
        }
    return combine_object_schemas([schema for schema in schemas if schema.get("type") != "array"])
