from django.conf import settings as django_settings

from tests.utils import remove_middleware  # make sure to remove middleware in these tests


def test_bad_response(client, caplog, monkeypatch):
    monkeypatch.setattr(django_settings, 'MIDDLEWARE', remove_middleware())
    client.get('/api/v1/animals')
