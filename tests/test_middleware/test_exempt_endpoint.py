import pytest
from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured

from django_swagger_tester.configuration import SwaggerTesterSettings
from tests.utils import patch_response_validation_middleware_settings


def test_endpoint_in_exempt_but_status_code_is_not(client, caplog, monkeypatch):
    monkeypatch.setattr(
        django_settings,
        'SWAGGER_TESTER',
        patch_response_validation_middleware_settings(
            'VALIDATION_EXEMPT_URLS', [{'url': '^api/v1/exempt-endpoint$', 'status_codes': [100]}]
        ),
    )
    settings = SwaggerTesterSettings()
    monkeypatch.setattr('django_swagger_tester.middleware.settings', settings)
    client.get('/api/v1/exempt-endpoint')
    # this message is logged after the exemption block in the middleware
    assert (
        'Validation skipped - response for GET request to /api/v1/exempt-endpoint has non-JSON content-type'
        in caplog.messages
    )


def test_endpoint_in_exempt_and_status_code_is_too(client, caplog, monkeypatch):
    monkeypatch.setattr(
        django_settings,
        'SWAGGER_TESTER',
        patch_response_validation_middleware_settings(
            'VALIDATION_EXEMPT_URLS', [{'url': '^api/v1/exempt-endpoint$', 'status_codes': [204]}]
        ),
    )
    settings = SwaggerTesterSettings()
    monkeypatch.setattr('django_swagger_tester.middleware.settings', settings)
    client.get('/api/v1/exempt-endpoint')
    assert (
        'Validation skipped: GET request to `/api/v1/exempt-endpoint` with status code 204 is in VALIDATION_EXEMPT_URLS'
        in caplog.messages
    )


def test_endpoint_in_exempt_and_wildcard_status_code(client, caplog, monkeypatch):
    monkeypatch.setattr(
        django_settings,
        'SWAGGER_TESTER',
        patch_response_validation_middleware_settings(
            'VALIDATION_EXEMPT_URLS', [{'url': '^api/v1/exempt-endpoint$', 'status_codes': ['*']}]
        ),
    )
    settings = SwaggerTesterSettings()
    monkeypatch.setattr('django_swagger_tester.middleware.settings', settings)
    client.get('/api/v1/exempt-endpoint')
    assert (
        'Validation skipped: GET request to `/api/v1/exempt-endpoint` with status code 204 is in VALIDATION_EXEMPT_URLS'
        in caplog.messages
    )


def test_invalid_status_code(client, caplog, monkeypatch):
    for item in ['100', 's', [], {}, None]:
        monkeypatch.setattr(
            django_settings,
            'SWAGGER_TESTER',
            patch_response_validation_middleware_settings(
                'VALIDATION_EXEMPT_URLS', [{'url': '^api/v1/exempt-endpoint$', 'status_codes': [item]}]
            ),
        )
        with pytest.raises(
            ImproperlyConfigured,
            match='Received an invalid status code in the response validation middleware settings. Status codes must be integers, or "*".',
        ):
            SwaggerTesterSettings()


def test_exempt_status_code(client, caplog, monkeypatch):
    monkeypatch.setattr(
        django_settings,
        'SWAGGER_TESTER',
        patch_response_validation_middleware_settings('VALIDATION_EXEMPT_STATUS_CODES', [204]),
    )
    settings = SwaggerTesterSettings()
    monkeypatch.setattr('django_swagger_tester.middleware.settings', settings)
    client.get('/api/v1/exempt-endpoint')
    assert 'Validation skipped: status code 204 is in VALIDATION_EXEMPT_STATUS_CODES' in caplog.messages
