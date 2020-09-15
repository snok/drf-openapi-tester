from django.conf import settings as django_settings

from django_swagger_tester.configuration import SwaggerTesterSettings
from tests.utils import patch_middleware_settings


def test_request_body_validated(client, caplog):
    client.post('/api/v1/items', data={'itemType': 'test'}, content_type='application/json')
    assert 'Validating request body for POST request to /api/v1/items' in caplog.messages


def test_bad_request_body(client, caplog, monkeypatch):
    monkeypatch.setattr(django_settings, 'SWAGGER_TESTER', patch_middleware_settings('REJECT_INVALID_REQUEST_BODIES', True))
    settings = SwaggerTesterSettings()
    monkeypatch.setattr('django_swagger_tester.middleware.settings', settings)

    response = client.post('/api/v1/items', data={'badKey': 'test'}, content_type='application/json')
    assert (
        response.content == b'Request body is invalid. The request body should have the following format: '
        b"{'itemType': 'truck'}. You need to add the missing key to your request body."
    )
