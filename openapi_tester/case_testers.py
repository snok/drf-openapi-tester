import logging
from typing import Callable, Optional

from openapi_tester.exceptions import CaseError
from inflection import camelize, underscore, humanize, dasherize

logger = logging.getLogger('openapi_tester')


def _create_tester(casing: str, handler: Callable[[str, Optional[bool]], str]) -> Callable[[str, str], None]:
    """ factory function for creating testers """
    def tester(key: str, origin: str) -> None:
        logger.debug(f'Verifying that {origin} key `{key}` is properly {humanize(casing)}')
        if key and not handler(key) == key:
            logger.error(f'{key} is not properly {humanize(casing)}')
            raise CaseError(key=key, case=casing, origin=origin, expected=handler(key))

    return tester


is_camel_case = _create_tester("camelCased", lambda x: camelize(x, False))
is_snake_case = _create_tester("snake_cased", underscore)
is_pascal_case = _create_tester("PascalCased", camelize)
is_kebab_case = _create_tester('kebab-cased', lambda x: dasherize(underscore(x)))
