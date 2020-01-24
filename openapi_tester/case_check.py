from typing import Union, Callable

from .exceptions import SpecificationError
from .utils import snake_case, camel_case


def test_case(case: Union[str, None]) -> Callable:
    """
    Returns the appropriate case check based on the `case` input parameter.

    :param case: str
    :return: function
    """
    return {'camel case': is_camel_case, 'snake case': is_snake_case, None: skip}[case]


def is_camel_case(key: str) -> None:
    """
    Asserts that a value is camelCased.

    :param key: str
    :return: None
    :raises: SpecificationError
    """
    if camel_case(key) != key:
        raise SpecificationError(f'The property `{key}` is not properly camelCased')


def is_snake_case(key: str) -> None:
    """
    Asserts that a value is snake_cased.

    :param key: str
    :return: None
    :raises: SpecificationError
    """
    if snake_case(key) != key:
        raise SpecificationError(f'The property `{key}` is not properly snake_cased')


def skip() -> None:
    """
    Skips case assertion.

    :return: None
    """
    pass
