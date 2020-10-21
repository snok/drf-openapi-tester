from django.core.exceptions import ImproperlyConfigured

import pytest

from django_swagger_tester.loaders import _LoaderBase


def test_valid_methods_pass():
    """
    Make sure valid methods pass the validation.
    """
    for method in ['get', 'post', 'put', 'patch', 'delete', 'options', 'head']:
        assert _LoaderBase().validate_method(method=method) == method


def test_invalid_methods_raise():
    """
    Make sure invalid methods raise the appropriate exception.
    """
    for method in ['test', '', -1, 22, 0.2, [], {}, (None,), None]:
        with pytest.raises(
            ImproperlyConfigured, match='is invalid. Should be one of: GET, POST, PUT, PATCH, DELETE, OPTIONS, HEAD.'
        ):
            _LoaderBase().validate_method(method=method)


def test_invalid_route():
    """
    Makes sure only strings are passed as valid route inputs.
    """
    for route in [[], (1, 2), 2, 2.0, {}, None]:
        with pytest.raises(ImproperlyConfigured):
            _LoaderBase().validate_string(route, 'route')


def test_invalid_status_codes():
    for status_code in range(-100, 100, 5):
        with pytest.raises(ImproperlyConfigured):
            _LoaderBase().validate_status_code(status_code)

    for status_code in range(506, 1000, 5):
        with pytest.raises(ImproperlyConfigured):
            _LoaderBase().validate_status_code(status_code)

    for status_code in [None, 'test', {}, []]:
        with pytest.raises(ImproperlyConfigured):
            _LoaderBase().validate_status_code(status_code)
