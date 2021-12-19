""" Case testers - this module includes helper functions to test key casing """
from __future__ import annotations

from typing import TYPE_CHECKING

from inflection import camelize, dasherize, underscore

from openapi_tester.exceptions import CaseError

if TYPE_CHECKING:
    from typing import Any, Callable


def _create_tester(casing: str, handler: Callable[[Any], str]) -> Callable[[str], None]:
    """factory function for creating testers"""

    def tester(key: str) -> None:
        stripped = key.strip()
        if stripped and handler(stripped) != stripped:
            raise CaseError(key=key, case=casing, expected=handler(key))

    return tester


def _camelize(string: str) -> str:
    return camelize(underscore(string), False)


def _pascalize(string: str) -> str:
    return camelize(underscore(string))


def _kebabize(string: str) -> str:
    return dasherize(underscore(string))


is_camel_case = _create_tester("camelCased", _camelize)
is_kebab_case = _create_tester("kebab-cased", _kebabize)
is_pascal_case = _create_tester("PascalCased", _pascalize)
is_snake_case = _create_tester("snake_cased", underscore)
