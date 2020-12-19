from django.core.exceptions import ImproperlyConfigured

import pytest

from django_swagger_tester.loaders import _LoaderBase
from django_swagger_tester.utils import get_endpoint_paths, resolve_path, unpack_response


def test_get_endpoint_paths():
    """
    Make sure the function returns a valid list of strings.
    """
    urls = list(set(get_endpoint_paths()))
    expected = [
        '/api/{version}/trucks/incorrect',
        '/api/{version}/{vehicle_type}/correct',
        '/api/{version}/{vehicle_type}/incorrect',
        '/api/{version}/vehicles',
        '/api/{version}/items',
        '/api/{version}/trucks/correct',
        '/api/{version}/snake-case/',
        '/api/{version}/animals',
        '/api/{version}/exempt-endpoint',
        '/en/api/{version}/i18n',
    ]
    assert all([url in expected for url in urls])
    assert len(expected) == len(urls)
