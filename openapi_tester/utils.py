import logging
import re

logger = logging.getLogger('openapi-tester')


def snake_case(string: str) -> str:
    """
    Converts an input string to snake_case.

    :param string: str
    :return: str
    """
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', re.sub('(.)([A-Z][a-z]+)', r'\1_\2', string)).lower()


def camel_case(string: str) -> str:
    """
    Converts an input string to camelCase.

    :param string: str
    :return: str
    """
    string = re.sub(r'^[\-_.]', '', str(string))
    if not string:
        return string
    return string[0].lower() + re.sub(r'[\-_.\s]([a-z])', lambda matched: matched.group(1).upper(), string[1:])
