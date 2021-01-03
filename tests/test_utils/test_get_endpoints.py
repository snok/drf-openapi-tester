from django.utils.translation import activate

from openapi_tester.utils import get_endpoint_paths


def test_get_endpoint_paths():
    """
    Make sure the function returns a valid list of strings.
    """
    activate('en')  # we need to force set locale for the i18n endpoint to work as expected

    actual = sorted(get_endpoint_paths())
    expected = sorted(
        [
            '/api/{version}/trucks/incorrect',
            '/api/{version}/cars/correct',
            '/api/{version}/cars/incorrect',
            '/api/{version}/vehicles',
            '/api/{version}/items',
            '/api/{version}/trucks/correct',
            '/api/{version}/snake-case/',
            '/api/{version}/animals',
            '/api/{version}/exempt-endpoint',
            '/en/api/{version}/i18n',
        ]
    )

    assert len(actual) == len(expected)
    for a, b in zip(actual, expected):
        assert a == b
