from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured

import pytest
from tests.utils import patch_response_validation_middleware_settings

from django_swagger_tester.configuration import SwaggerTesterSettings


def test_improperly_configured_if_not_in_installed_apps(client, monkeypatch):
    """
    Test that the app will fail if `is_installed('django_guid')` is `False`.
    """
    monkeypatch.setattr('django_swagger_tester.middleware.apps.is_installed', lambda x: False)
    with pytest.raises(ImproperlyConfigured, match='django_swagger_tester must be listed in your installed apps'):
        client.get('/')


def test_debug_false(client, caplog, monkeypatch):
    monkeypatch.setattr(
        django_settings, 'SWAGGER_TESTER', patch_response_validation_middleware_settings('DEBUG', False)
    )
    settings = SwaggerTesterSettings()
    monkeypatch.setattr('django_swagger_tester.middleware.settings', settings)
    client.get('/api/v1/cars/correct')
    assert len(caplog.messages) == 0


def test_bad_path(client, caplog):
    client.get('/api/v1/cars/corrects')
    assert 'Validation skipped - GET request to /api/v1/cars/corrects failed to resolve' in caplog.messages


def test_non_existent_class_method(client, caplog):
    client.options('/api/v1/cars/correct')
    assert 'OPTIONS request method does not exist in the view class' in caplog.messages
