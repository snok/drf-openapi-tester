from django_swagger_tester.utils import get_paths


def test_get_paths():
    """
    Make sure the function returns a valid list of strings.
    """
    urls = list(set(get_paths()))
    expected = [
        '/api/v1/trucks/incorrect/',
        '/api/v1/{vehicle_type}/correct/',
        '/api/v1/{vehicle_type}/incorrect/',
        '/api/v1/vehicles/',
        '/api/v1/trucks/correct/',
    ]
    assert [url in expected for url in urls]
    assert len(expected) == len(urls)
