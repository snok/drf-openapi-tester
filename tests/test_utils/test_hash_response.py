from copy import deepcopy

x = {
    'id': 1,
    'a': {'a': {'id': 2500000, 'title': 'title'}, 'b': {'id': 2500000, 'title': 'title'}},
    'b': {
        'a': '5005f30e-95c5-a860-29dc-9aa8ead698e0',
        'b': '5005f30e-95c5-a860-29dc-9aa8ead698e0',
        'c': {
            'a': '5005f30e-95c5-a860-29dc-9aa8ead698e0',
            'b': '5005f30e-95c5-a860-29dc-9aa8ead698e0',
            'c': 'name',
            'd': 'name2',
            'e': 'code',
            'registered': '2020-06-17T16:17:35.519707+02:00',
            'modified': '2020-06-17T16:17:35.519707+02:00',
        },
        'd': 'displayname',
        'e': 'firstname',
        'f': 'lastname',
        'g': 'fullname',
        'h': 'username',
        'i': 'email',
        'j': 'title',
        'k': 'upn',
        'l': 'phone',
        'm': 'role',
        'n': False,
        'registered': '2020-06-17T16:17:35.519707+02:00',
        'modified': '2020-06-17T16:17:35.519707+02:00',
    },
    'c': {
        'a': '5005f30e-95c5-a860-29dc-9aa8ead698e0',
        'b': '5005f30e-95c5-a860-29dc-9aa8ead698e0',
        'c': {
            'a': '5005f30e-95c5-a860-29dc-9aa8ead698e0',
            'b': '5005f30e-95c5-a860-29dc-9aa8ead698e0',
            'c': 'name',
            'd': 'name2',
            'e': 'code',
            'registered': '2020-06-17T16:17:35.519707+02:00',
            'modified': '2020-06-17T16:17:35.519707+02:00',
        },
        'd': 'displayname',
        'e': 'firstname',
        'f': 'lastname',
        'g': 'fullname',
        'h': 'username',
        'i': 'email',
        'j': 'title',
        'k': 'upn',
        'l': 'phone',
        'm': 'role',
        'n': False,
        'registered': '2020-06-17T16:17:35.519707+02:00',
        'modified': '2020-06-17T16:17:35.519707+02:00',
    },
    'd': {
        'a': '5005f30e-95c5-a860-29dc-9aa8ead698e0',
        'b': 'name',
        'c': 'code',
        'registered': '2020-06-17T16:17:35.519707+02:00',
        'modified': '2020-06-17T16:17:35.519707+02:00',
    },
    'registered': '2020-06-17T16:17:35.519707+02:00',
    'modified': '2020-06-17T16:17:35.519707+02:00',
}

from django_swagger_tester.utils import hash_response


def test_hash_response():
    assert hash_response(x) == hash_response(x)
    y = deepcopy(x)
    y['id'] = None
    assert hash_response(x) != hash_response(y)
