""" Utils Module - this file contains utility functions used in multiple places """
from typing import Any, Dict, Iterable, List


def merge_objects(dictionaries: List[Dict[str, Any]]) -> Dict[str, Any]:
    """ helper function to deep merge objects """
    output: Dict[str, Any] = {}
    for dictionary in dictionaries:
        for key, value in dictionary.items():
            if isinstance(value, dict) and "allOf" in value:
                all_of = merge_objects(value.pop("allOf"))
                value = merge_objects([value, all_of])
            if key not in output:
                output[key] = value
                continue
            current_value = output[key]
            if isinstance(current_value, list) and isinstance(value, list):
                output[key] = list({*output[key], *value})
            if isinstance(current_value, dict) and isinstance(value, dict):
                output[key] = merge_objects([current_value, value])
    return output


def combine_object_schemas(schemas: List[dict]) -> Dict[str, Any]:
    properties = merge_objects([schema.get("properties", {}) for schema in schemas])
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
    return merge_objects([schema for schema in schemas if schema.get("type") not in ["object", "array", None]])


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

    # def __init__(
    #     self,
    #     message: str,
    #     response: Any,
    #     schema: dict,
    #     hint: str = "",
    #     reference: str = "",
    # ) -> None:
    #     from openapi_tester.schema_converter import SchemaToPythonConverter
    #
    #     converted_schema = SchemaToPythonConverter(schema, with_faker=False).result
    #     super().__init__(
    #         self.format(
    #             response=sort_object(response),
    #             example_item=sort_object(converted_schema),
    #             hint=hint,
    #             message=message,
    #             reference=reference,
    #         )
    #     )
    #
    # @staticmethod
    # def format(example_item: Any, response: Any, reference: str, message: str, hint: str) -> str:
    #     """
    #     Formats and returns a standardized error message for easy debugging.
    #     """
    #
    #     expected = json.dumps(example_item).replace('"', "")
    #     received = json.dumps(response)
    #
    #     msg = [
    #         f"{message}\n\n",
    #         f"Expected: {expected}\n\n",
    #         f"Received: {received}\n\n",
    #     ]
    #     if hint:
    #         msg += [f"Hint: {hint}\n\n"]
    #     if reference:
    #         msg += [
    #             f"Sequence: {reference}\n",
    #         ]
    #     return "".join(msg)
