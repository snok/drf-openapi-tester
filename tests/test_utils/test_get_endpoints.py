import pytest
from django.core.exceptions import ImproperlyConfigured

from django_swagger_tester.loaders import _LoaderBase
from django_swagger_tester.utils import get_endpoint_paths, unpack_response, resolve_path


def test_get_endpoint_paths():
    """
    Make sure the function returns a valid list of strings.
    """
    urls = list(set(get_endpoint_paths()))
    expected = [
        '/api/v1/trucks/incorrect/',
        '/api/v1/{vehicle_type}/correct/',
        '/api/v1/{vehicle_type}/incorrect/',
        '/api/v1/vehicles/',
        '/api/v1/items/',
        '/api/v1/trucks/correct/',
    ]
    assert [url in expected for url in urls]
    assert len(expected) == len(urls)
