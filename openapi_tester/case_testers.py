from __future__ import annotations

from collections.abc import Callable
from typing import Any

from inflection import camelize, dasherize, underscore

from openapi_tester.exceptions import CaseError


def _create_tester(casing: str, handler: Callable[[Any], str]) -> Callable[[str], None]:
    """ factory function for creating testers """

    def tester(key: str) -> None:
        stripped = key.strip()
        if len(stripped) and not handler(stripped) == stripped:
            raise CaseError(key=key, case=casing, expected=handler(key))

    return tester


def _camelize(s: str) -> str:
    return camelize(underscore(s), False)


def _pascalize(s: str) -> str:
    return camelize(underscore(s))


def _kebabize(s: str) -> str:
    return dasherize(underscore(s))


is_camel_case = _create_tester('camelCased', _camelize)
is_kebab_case = _create_tester('kebab-cased', _kebabize)
is_pascal_case = _create_tester('PascalCased', _pascalize)
is_snake_case = _create_tester('snake_cased', underscore)
