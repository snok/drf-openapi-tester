""" Utils Module - this file contains utility functions used in multiple places """
from typing import Any, Dict, List


def combine_sub_schemas(schemas: List[dict]) -> Dict[str, Any]:
    array_schemas = [schema for schema in schemas if schema.get("type") == "array"]
    if array_schemas:
        items_lists = [schema.get("items", {}) for schema in array_schemas]
        return {"type": "array", "items": [item for item_list in items_lists for item in item_list]}
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
