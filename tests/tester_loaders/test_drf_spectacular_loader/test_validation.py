import pytest
from django.core.exceptions import ImproperlyConfigured

from response_tester.loaders import DrfSpectacularSchemaLoader


def test_drf_spectacular_not_in_installed_apps(monkeypatch):
    """
    Verify that validation raises an exception if the package is not installed.
    """

    monkeypatch.setattr('django.conf.settings.INSTALLED_APPS', [])

    with pytest.raises(ImproperlyConfigured, match='is missing from INSTALLED_APPS'):
        DrfSpectacularSchemaLoader()
