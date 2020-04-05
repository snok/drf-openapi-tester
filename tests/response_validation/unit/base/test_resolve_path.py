import pytest

from django_swagger_tester.response_validation.base.base import SwaggerTestBase

base = SwaggerTestBase()
paths = [
    '/api/v1/cars/correct/',
    '/api/v1/trucks/correct/',
    '/api/v1/cars/incorrect/',
    '/api/v1/trucks/incorrect/'
]


def test_successful_resolve() -> None:
    """
    This should run without errors.
    """
    for path in paths:
        base._resolve_path(path)


def test_successful_resolve_despite_missing_leading_slash():
    """
    A path should resolve despite missing a leading slash.
    """
    for path in paths:
        base._resolve_path(path[1:])


def test_successful_resolve_despite_missing_trailing_slash():
    """
    A trailing slash isn't always necessary, but when it is, a path missing its trailing slash should still resolve successfully.
    """
    for path in paths:
        base._resolve_path(path[:-1])


def test_path_suggestions():
    """
    When a resolve fails, we want to output useful output.
    """
    with pytest.raises(ValueError, match='Did you mean one of these?'):
        base._resolve_path('trucks/correct')


def test_no_path_suggestions():
    """
    Make sure the appropriate error is raised.
    """
    with pytest.raises(ValueError, match='Could not resolve path'):
        base._resolve_path('this is not a path')
