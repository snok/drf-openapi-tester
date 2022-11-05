"""
Utils Module - this file contains utility functions used in multiple places.
"""
from __future__ import annotations

from copy import deepcopy
from itertools import chain, combinations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Iterator, Sequence


def merge_objects(dictionaries: Sequence[dict[str, Any]]) -> dict[str, Any]:
    """
    Deeply merge objects.
    """
    output: dict[str, Any] = {}
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


def normalize_schema_section(schema_section: dict[str, Any]) -> dict[str, Any]:
    """
    Remove allOf and handle edge uses of oneOf.
    """
    output: dict[str, Any] = deepcopy(schema_section)
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


def lazy_combinations(options_list: Sequence[dict[str, Any]]) -> Iterator[dict]:
    """
    Lazily evaluate possible combinations.
    """
    for i in range(2, len(options_list) + 1):
        for combination in combinations(options_list, i):
            yield merge_objects(combination)
