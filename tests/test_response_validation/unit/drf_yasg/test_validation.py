import pytest
from django.core.exceptions import ImproperlyConfigured

from django_swagger_tester.drf_yasg.loader import LoadDrfYasgSchema


def test_validation():
    """
    Verify that validation runs successfully for the demo project.
    """
    base = LoadDrfYasgSchema('api/v1/cars/correct', 'get', status_code=200)
    assert base.validation() is None


def test_drf_yasg_not_installed(monkeypatch):
    """
    Verify that validation raises an exception if the package isnt installed.
    """
    import sys

    # Mock away the drf_yasg dependency
    temp = sys.modules['drf_yasg']
    sys.modules['drf_yasg'] = None

    with pytest.raises(
        ImproperlyConfigured,
        match='The package `drf_yasg` is required. Please run `pip install drf_yasg` to install it.',
    ):
        LoadDrfYasgSchema('api/v1/cars/correct', 'get', status_code=200)

    sys.modules['drf_yasg'] = temp


def test_drf_yasg_not_in_installed_apps(monkeypatch):
    """
    Verify that validation raises an exception if the package is not installed.
    """

    class MockAppConfigs:
        @staticmethod
        def keys():
            return []

    class MockedApps:
        app_configs = MockAppConfigs

    monkeypatch.setattr('django_swagger_tester.drf_yasg.loader.apps', MockedApps())

    with pytest.raises(ImproperlyConfigured, match='is missing from INSTALLED_APPS'):
        LoadDrfYasgSchema('api/v1/cars/correct', 'get', status_code=200)
