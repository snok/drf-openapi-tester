""" Utils Module - this file contains utility functions used in multiple places """
from typing import Any, Dict, Sequence


def merge_objects(dictionaries: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
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
                output[key] = [*output[key], *value]
            if isinstance(current_value, dict) and isinstance(value, dict):
                output[key] = merge_objects([current_value, value])
    return output


def normalize_schema_section(schema_section: dict) -> dict:
    """ helper method to remove allOf and handle edge uses of oneOf"""
    output: Dict[str, Any] = {**schema_section}
    if "allOf" in schema_section:
        all_of = schema_section.pop("allOf")
        schema_section = {**schema_section, **merge_objects(all_of)}
    if schema_section.get("oneOf") and all(item.get("enum") for item in schema_section["oneOf"]):
        # handle the way drf-spectacular is doing enums
        one_of = schema_section.pop("oneOf")
        schema_section = {**schema_section, **merge_objects(one_of)}
    for key, value in output.items():
        if isinstance(value, dict):
            output[key] = normalize_schema_section(value)
        elif isinstance(value, list):
            output[key] = [normalize_schema_section(entry) if isinstance(entry, dict) else entry for entry in value]
    return schema_section
