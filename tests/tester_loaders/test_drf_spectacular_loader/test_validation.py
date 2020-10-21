from django.core.exceptions import ImproperlyConfigured

import pytest

from django_swagger_tester.loaders import DrfSpectacularSchemaLoader

base = DrfSpectacularSchemaLoader()
base.set_schema(base.load_schema())


def test_drf_spectacular_loader_validation():
    """
    Verify that validation runs successfully for the demo project.
    """
    assert base.validation() is None


def test_drf_spectacular_not_installed(monkeypatch):
    """
    Verify that validation raises an exception if the package isnt installed.
    """
    import sys

    # Mock away the drf_spectacular dependency
    temp = sys.modules['drf_spectacular']
    sys.modules['drf_spectacular'] = None

    with pytest.raises(
        ImproperlyConfigured,
        match='The package `drf_spectacular` is required. Please run `pip install drf_spectacular` to install it.',
    ):
        base.validation()
    sys.modules['drf_spectacular'] = temp


def test_drf_spectacular_not_in_installed_apps(monkeypatch):
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
