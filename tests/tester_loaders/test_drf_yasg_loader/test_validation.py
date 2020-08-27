import pytest
from django.core.exceptions import ImproperlyConfigured

from django_swagger_tester.loaders import DrfYasgSchemaLoader

base = DrfYasgSchemaLoader()
base.set_schema(base.load_schema())


def test_drf_yasg_loader_validation():
    """
    Verify that validation runs successfully for the demo project.
    """
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
        base.validation()
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

    monkeypatch.setattr('django_swagger_tester.loaders.apps', MockedApps())

    with pytest.raises(ImproperlyConfigured, match='is missing from INSTALLED_APPS'):
        base.validation()
