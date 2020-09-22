from django.conf import settings as django_settings

from tests.utils import remove_middleware  # make sure to remove middleware in these tests


def test_bad_response(client, caplog, monkeypatch):
    monkeypatch.setattr(django_settings, 'MIDDLEWARE', remove_middleware())
    client.get('/api/v1/animals')
    assert any(
        '''Bad response returned for GET request to /api/v1/animals. Error: Item is misspecified:\n\nSummary\n''' in message
        for message in caplog.messages
    )


def test_204_no_content(client, monkeypatch):
    # this used to trigger an error before we fixed 204 conditional copy-response-logic
    monkeypatch.setattr(django_settings, 'MIDDLEWARE', remove_middleware())
    client.delete('/api/v1/animals')
