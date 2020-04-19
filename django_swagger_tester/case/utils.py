import logging
from typing import Callable, List

logger = logging.getLogger('django_swagger_tester')


def set_ignored_keys(**kwargs) -> List[str]:
    """
    Lets users pass a list of string that will not be checked by case-check.
    For example, validate_response(..., ignore_case=["List", "OF", "improperly cased", "kEYS"]).
    """
    if 'ignore_case' in kwargs:
        return kwargs['ignore_case']
    return []


def conditional_check(key: str, function: Callable, ignored_keys: list) -> None:
    """
    Checks a keys case if the key is not ignored.

    Put this in its own function so that we're consistent in response and schema validation handling.

    :param key: dictionary key
    :param function: case check callable
    :param ignored_keys: list of ignored values - values that shouldn't be checked
    raises: django_swagger_tester.exceptions.CaseError
    """
    if key not in ignored_keys:
        function(key)
    else:
        logger.debug('Skipping case check for ignored key `%s`', key)
