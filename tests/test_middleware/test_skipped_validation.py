"""
Requests in these tests should not be handled by the middleware.
"""

from django.conf import settings as django_settings

from django_swagger_tester.configuration import SwaggerTesterSettings
from tests.utils import patch_response_validation_middleware_settings


def test_exempt_url(client, caplog, monkeypatch):
    monkeypatch.setattr(
        django_settings,
        'SWAGGER_TESTER',
        patch_response_validation_middleware_settings(
            'VALIDATION_EXEMPT_URLS', [{'url': '^api/v1/cars/correct$', 'status_codes': ['*']}]
        ),
    )
    settings = SwaggerTesterSettings()
    monkeypatch.setattr('django_swagger_tester.middleware.settings', settings)
    client.get('/api/v1/cars/correct')
    assert (
        'Validation skipped: GET request to `/api/v1/cars/correct` with status code 200 is in VALIDATION_EXEMPT_URLS'
        in caplog.messages
    )


def test_non_endpoint_options_request(client, caplog):
    """
    Makes sure these types of requests are *not* handled by the middleware.
    """
    for path in ['', 'test']:
        client.options(path)
        assert 'Validation skipped: `/%s` is not a relevant endpoint' % path in caplog.messages
