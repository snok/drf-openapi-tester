import logging
from typing import Any, Callable

from inflection import camelize, dasherize, underscore

from openapi_tester.exceptions import CaseError

logger = logging.getLogger('openapi_tester')


def _create_tester(casing: str, handler: Callable[[Any], str]) -> Callable[[str, str], None]:
    """ factory function for creating testers """

    def tester(key: str, origin: str = 'schema') -> None:
        stripped = key.strip()
        logger.debug(f'Verifying that {origin} key `{stripped}` is properly {casing}')
        if len(stripped) and not handler(stripped) == stripped:
            logger.error(f'{stripped} is not properly {casing}')
            raise CaseError(key=key, case=casing, origin=origin, expected=handler(key))

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
