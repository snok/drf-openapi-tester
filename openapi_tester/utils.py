""" Utils Module - this file contains utility functions used in multiple places """
from copy import deepcopy
from itertools import chain, combinations
from typing import Any, Dict, Iterator, Sequence


def merge_objects(dictionaries: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    """ helper function to deep merge objects """
    output: Dict[str, Any] = {}
    for dictionary in dictionaries:
        for key, value in dictionary.items():
            if key not in output:
                output[key] = value
                continue
            current_value = output[key]
            if isinstance(current_value, list) and isinstance(value, list):
                output[key] = list(chain(output[key], value))
                continue
            if isinstance(current_value, dict) and isinstance(value, dict):
                output[key] = merge_objects([current_value, value])
                continue
    return output


def normalize_schema_section(schema_section: dict) -> dict:
    """ helper method to remove allOf and handle edge uses of oneOf"""
    output: Dict[str, Any] = deepcopy(schema_section)
    if output.get("allOf"):
        all_of = output.pop("allOf")
        output = {**output, **merge_objects(all_of)}
    if output.get("oneOf") and all(item.get("enum") for item in output["oneOf"]):
        # handle the way drf-spectacular is doing enums
        one_of = output.pop("oneOf")
        output = {**output, **merge_objects(one_of)}
    for key, value in output.items():
        if isinstance(value, dict):
            output[key] = normalize_schema_section(value)
        elif isinstance(value, list):
            output[key] = [normalize_schema_section(entry) if isinstance(entry, dict) else entry for entry in value]
    return output


def lazy_combinations(options_list: Sequence[Dict[str, Any]]) -> Iterator[dict]:
    """ helper to lazy evaluate possible permutations of possible combinations  """
    for i in range(2, len(options_list) + 1):
        for combination in combinations(options_list, i):
            yield merge_objects(combination)
