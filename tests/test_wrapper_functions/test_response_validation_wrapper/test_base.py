from django.conf import settings as django_settings

from tests.utils import remove_middleware  # make sure to remove middleware in these tests


def test_bad_response(client, caplog, monkeypatch):
    monkeypatch.setattr(django_settings, 'MIDDLEWARE', remove_middleware())
    client.get('/api/v1/animals')
    assert (
        '''Bad response returned for GET request to /api/v1/animals. Error: Item is misspecified:\n\nSummary\n------------------------------------------------------------------------------------------\n\nError:      Mismatched types. Expected item to be <class 'list'> but found <class 'dict'>.\n\nExpected:   [{'test': 'test', 'test2': 'test2'}]\nReceived:   {'bird': 'mixed reviews', 'dog': 'very cool', 'monkey': 'very cool', 'spider': 'not cool'}\n\nHint:       You might need to wrap your response item in a list, or remove the excess list layer from your documented response.\n            \nSequence:   init\n\n------------------------------------------------------------------------------------------\n'''
        in caplog.messages
    )
