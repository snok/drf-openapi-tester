"""
Requests in these tests should not trigger request body validation in the middleware.
"""

from django.conf import settings as django_settings

from django_swagger_tester.configuration import SwaggerTesterSettings
from tests.utils import patch_middleware_settings


def test_setting_turned_off(client, caplog, monkeypatch):
    monkeypatch.setattr(django_settings, 'SWAGGER_TESTER', patch_middleware_settings('VALIDATE_REQUEST_BODY', False))
    settings = SwaggerTesterSettings()
    monkeypatch.setattr('django_swagger_tester.middleware.settings', settings)
    client.get('/api/v1/cars/correct')
    assert 'Skipping request body validation: VALIDATE_REQUEST_BODY is False' in caplog.messages


def test_no_request_body(client, caplog):
    for path in ['/api/v1/cars/correct', '/api/v1/cars/incorrect']:
        client.options(path)
        assert (
            'Skipping request body validation: OPTIONS request to `/api/v1/cars/correct` doesn\'t contain a request body'
            in caplog.messages
        )

        client.get(path)
        assert (
            'Skipping request body validation: GET request to `%s` doesn\'t contain a request body' % path in caplog.messages
        )


def test_non_json_request_body(client, caplog):
    client.post('/api/v1/cars/correct', data={'test': 'test'})
    assert (
        'Skipping request body validation: POST request to `/api/v1/cars/correct` has a non-JSON content type'
        in caplog.messages
    )


def test_json_request_body(client, caplog):
    """
    Here to validate the above test.
    """
    client.post('/api/v1/cars/correct', data={'test': 'test'}, content_type='application/json')
    assert (
        'Skipping request body validation: POST request to `/api/v1/cars/correct` has a non-JSON content type'
        not in caplog.messages
    )
