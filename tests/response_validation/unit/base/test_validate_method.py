import pytest

from django_swagger_tester.utils import validate_method


def test_valid_methods_pass():
    """
    Make sure valid methods pass the validation.
    """
    for method in ['get', 'post', 'put', 'patch', 'delete', 'options', 'head']:
        assert validate_method(method=method) == method


def test_invalid_methods_raise():
    """
    Make sure invalid methods raise the appropriate exception.
    """
    for method in ['test', '', -1, 22, 0.2, [], {}, (None,), None]:
        with pytest.raises(
            ValueError, match='is invalid. Should be one of: GET, POST, PUT, PATCH, DELETE, OPTIONS, HEAD.'
        ):
            validate_method(method=method)
