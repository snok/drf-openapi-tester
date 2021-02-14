""" Utils Module - this file contains utility functions used in multiple places """
from typing import Any, Dict, Iterable, List


def merge_dicts(dictionaries: List[Dict[str, Any]]) -> Dict[str, Any]:
    output: Dict[str, Any] = {}
    for dictionary in dictionaries:
        for key, value in dictionary.items():
            if "allOf" in value:
                output[key] = combine_sub_schemas(value["allOf"])
            elif key in output and isinstance(value, dict):
                output[key] = {**output[key], **value}
            elif key in output and isinstance(value, list):
                output[key] = [*output[key], *value]
            else:
                output[key] = value
    return output


def combine_object_schemas(schemas: List[dict]) -> Dict[str, Any]:
    properties = merge_dicts([schema.get("properties", {}) for schema in schemas])
    required_list = [schema.get("required", []) for schema in schemas]
    required = list({key for required in required_list for key in required})
    return {"type": "object", "required": required, "properties": properties}


def combine_sub_schemas(schemas: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    array_schemas = [schema for schema in schemas if schema.get("type") == "array"]
    object_schemas = [schema for schema in schemas if schema.get("type") == "object" or not schema.get("type")]
    if array_schemas:
        return {
            "type": "array",
            "items": combine_sub_schemas([schema.get("items", {}) for schema in array_schemas]),
        }
    if object_schemas:
        return combine_object_schemas(object_schemas)
    return merge_dicts([schema for schema in schemas if schema.get("type") not in ["object", "array", None]])


def sort_object(data_object: Any) -> Any:
    """ helper function to sort objects """
    if isinstance(data_object, dict):
        for key, value in data_object.items():
            if isinstance(value, (dict, list)):
                data_object[key] = sort_object(value)
        return dict(sorted(data_object.items()))
    if isinstance(data_object, list) and data_object:
        if not all(isinstance(entry, type(data_object[0])) for entry in data_object):
            return data_object
        if isinstance(data_object[0], (dict, list)):
            return [sort_object(entry) for entry in data_object]
        return sorted(data_object)
    return data_object
