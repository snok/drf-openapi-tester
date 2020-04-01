from django_swagger_tester.utils import list_project_urls


def test_list_project_urls():
    """
    Make sure the function returns a valid list of strings.
    """
    urls = list_project_urls()
    assert urls == [
        'swagger/',
        'redoc/',
        'api/v1/<vehicle_type:vehicle_type>/correct/',
        'api/v1/<vehicle_type:vehicle_type>/incorrect/',
        'api/v1/trucks/correct/',
        'api/v1/trucks/incorrect/',
        'api/v1/vehicles/'
    ]
