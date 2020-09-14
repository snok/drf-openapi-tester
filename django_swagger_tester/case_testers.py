import logging
import re

from django_swagger_tester.exceptions import CaseError

logger = logging.getLogger('django_swagger_tester')


def is_camel_case(key: str, origin: str) -> None:
    """
    Asserts that a value is camelCased.

    :param key: The key to be tested
    :param origin: Where the key came from (e.g., response or schema)
    :raises: django_swagger_tester.exceptions.CaseError
    """
    logger.debug('Verifying that %s key `%s` is properly camel cased', origin, key)
    if len(key) == 0:
        return
    if len(key) == 1 and (key.isalpha() is False or (key.isalpha() is True and key != key.casefold())):
        logger.error('`%s` is not properly camel cased', key)
        raise CaseError(key=key, case='camelCased', origin=origin)
    else:
        camel_cased_key = key[0].lower() + re.sub(r'[\-_.\s]([a-z])', lambda matched: matched.group(1).upper(), key[1:])
        if camel_cased_key != key:
            logger.error('`%s` is not properly camel cased', key)
            raise CaseError(key=key, case='camelCased', origin=origin)


def is_snake_case(key: str, origin: str) -> None:
    """
    Asserts that a value is snake_cased.

    :param key: The key to be tested
    :param origin: Where the key came from (e.g., response or schema)
    :raises: django_swagger_tester.exceptions.CaseError
    """
    logger.debug('Verifying that %s key `%s` is properly snake cased', origin, key)
    if len(key) == 0:
        return
    if len(key) == 1 and (key.isalpha() is False or (key.isalpha() is True and key != key.casefold())):
        logger.error('%s is not snake cased', key)
        raise CaseError(key=key, case='snake_cased', origin=origin)
    snake_cased_key = (
        re.sub('([a-z0-9])([A-Z])', r'\1_\2', re.sub('(.)(-)([A-Z][a-z]+)', r'\1_\2', key))
        .lower()
        .replace('-', '_')
        .replace(' ', '')
    )
    if snake_cased_key != key:
        logger.error('%s is not snake cased', key)
        raise CaseError(key=key, case='snake_cased', origin=origin)


def is_kebab_case(key: str, origin: str) -> None:
    """
    Asserts that a value is kebab-cased.

    :param key: The key to be tested
    :param origin: Where the key came from (e.g., response or schema)
    :raises: django_swagger_tester.exceptions.CaseError
    """
    logger.debug('Verifying that %s key `%s` is properly kebab cased', origin, key)
    if len(key) == 0:
        return
    if len(key) == 1 and (key.isalpha() is False or (key.isalpha() is True and key != key.casefold())):
        logger.error('%s is not kebab cased', key)
        raise CaseError(key=key, case='kebab-cased', origin=origin)
    kebab_cased_key = (
        re.sub('([a-z0-9])([A-Z])', r'\1-\2', re.sub('(.)([A-Z][a-z]+)', r'\1-\2', key))
        .lower()
        .replace('_', '-')
        .replace(' ', '')
    )
    if kebab_cased_key != key:
        logger.error('%s is not kebab cased', key)
        raise CaseError(key=key, case='kebab-cased', origin=origin)


def is_pascal_case(key: str, origin: str) -> None:
    """
    Asserts that a value is PascalCased.

    :param key: The key to be tested
    :param origin: Where the key came from (e.g., response or schema)
    :raises: django_swagger_tester.exceptions.CaseError
    """
    logger.debug('Verifying that %s key `%s` is properly pascal cased', origin, key)
    if len(key) == 0:
        return
    if len(key) == 1 and (key.isalpha() is False or (key.isalpha() is True and key != key.upper())):
        logger.error('%s is not pascal cased', key)
        raise CaseError(key=key, case='PascalCased', origin=origin)
    pascal_cased_key = key[0].upper() + re.sub(r'[\-_.\s]([a-z])', lambda matched: matched.group(1).upper(), key[1:])
    if pascal_cased_key != key:
        logger.error('%s is not pascal cased', key)
        raise CaseError(key=key, case='PascalCased', origin=origin)
