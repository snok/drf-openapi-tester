import logging
import re

from django_swagger_tester.exceptions import CaseError

logger = logging.getLogger('django_swagger_tester')


def _case_error_message(case: str, key: str) -> str:
    """
    Returns an appropriate error message.
    """
    return (
        f'The property `{key}` is not properly {case}\n\n'
        f'If this is intentional, you can skip case validation by adding `ignore_case=[\'{key}\']` to your function call'
    )


def is_camel_case(key: str) -> None:
    """
    Asserts that a value is camelCased.

    :param key: str
    :return: None
    :raises: django_swagger_tester.exceptions.CaseError
    """
    logger.debug('Verifying that `%s` is properly camel cased', key)
    if len(key) == 0:
        return
    if len(key) == 1 and (key.isalpha() is False or (key.isalpha() is True and key != key.casefold())):
        logger.error('`%s` is not properly camel cased', key)
        raise CaseError(_case_error_message(key=key, case='camelCased'))
    else:
        camel_cased_key = key[0].lower() + re.sub(r'[\-_.\s]([a-z])', lambda matched: matched.group(1).upper(), key[1:])
        if camel_cased_key != key:
            logger.error('`%s` is not properly camel cased', key)
            raise CaseError(_case_error_message(key=key, case='camelCased'))


def is_snake_case(key: str) -> None:
    """
    Asserts that a value is snake_cased.

    :param key: str
    :return: None
    :raises: django_swagger_tester.exceptions.CaseError
    """
    logger.debug('Verifying that `%s` is properly snake cased', key)
    if len(key) == 0:
        return
    if len(key) == 1 and (key.isalpha() is False or (key.isalpha() is True and key != key.casefold())):
        logger.error('%s is not snake cased', key)
        raise CaseError(_case_error_message(key=key, case='snake_cased'))
    snake_cased_key = (
        re.sub('([a-z0-9])([A-Z])', r'\1_\2', re.sub('(.)(-)([A-Z][a-z]+)', r'\1_\2', key))
        .lower()
        .replace('-', '_')
        .replace(' ', '')
    )
    if snake_cased_key != key:
        logger.error('%s is not snake cased', key)
        raise CaseError(_case_error_message(key=key, case='snake_cased'))


def is_kebab_case(key: str) -> None:
    """
    Asserts that a value is kebab-cased.

    :param key: str
    :return: None
    :raises: django_swagger_tester.exceptions.CaseError
    """
    logger.debug('Verifying that `%s` is properly kebab cased', key)
    if len(key) == 0:
        return
    if len(key) == 1 and (key.isalpha() is False or (key.isalpha() is True and key != key.casefold())):
        logger.error('%s is not kebab cased', key)
        raise CaseError(_case_error_message(key=key, case='kebab-cased'))
    kebab_cased_key = (
        re.sub('([a-z0-9])([A-Z])', r'\1-\2', re.sub('(.)([A-Z][a-z]+)', r'\1-\2', key))
        .lower()
        .replace('_', '-')
        .replace(' ', '')
    )
    if kebab_cased_key != key:
        logger.error('%s is not kebab cased', key)
        raise CaseError(_case_error_message(key=key, case='kebab-cased'))


def is_pascal_case(key: str) -> None:
    """
    Asserts that a value is PascalCased.

    :param key: str
    :return: None
    :raises: django_swagger_tester.exceptions.CaseError
    """
    logger.debug('Verifying that `%s` is properly pascal cased', key)
    if len(key) == 0:
        return
    if len(key) == 1 and (key.isalpha() is False or (key.isalpha() is True and key != key.upper())):
        logger.error('%s is not pascal cased', key)
        raise CaseError(_case_error_message(key=key, case='PascalCased'))
    pascal_cased_key = key[0].upper() + re.sub(r'[\-_.\s]([a-z])', lambda matched: matched.group(1).upper(), key[1:])
    if pascal_cased_key != key:
        logger.error('%s is not pascal cased', key)
        raise CaseError(_case_error_message(key=key, case='PascalCased'))
