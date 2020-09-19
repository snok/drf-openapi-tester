from copy import deepcopy

import pytest
import yaml
from django.core.exceptions import ImproperlyConfigured

from demo import settings
from django_swagger_tester.configuration import settings as _settings
from django_swagger_tester.loaders import _LoaderBase
from tests.types import bool_type, integer_type, number_type, string_type
from tests.utils import MockRoute


def loader(path):
    with open(str(settings.BASE_DIR.parent) + path, 'r') as f:
        return _settings.loader_class.replace_refs(yaml.load(f, Loader=yaml.FullLoader))


schema = loader('/tests/drf_yasg_reference.yaml')
base = _LoaderBase()
base.set_schema(schema)


def test_create_dict_from_schema(monkeypatch):
    """
    Makes sure we're able to accurately serialize an object.
    """
    expected = {
        'title': 'string',
        'author': 1,
        'body': 'string',
        'slug': 'string',
        'date_created': 'string',
        'date_modified': 'string',
        'read_only_nullable': 'string',
        'references': {'': 'string'},
        'uuid': 'string',
        'cover': 'string',
        'cover_name': 'string',
        'article_type': 1,
        'group': 'string',
        'original_group': 'string',
    }
    monkeypatch.setattr(base, 'get_route', MockRoute)
    response_schema = base.get_response_schema_section(route='/articles/', method='POST', status_code=201)
    assert base.create_dict_from_schema(response_schema) == expected


def test_iterate_schema_dict(caplog):
    """
    Tests that we're parsing schema objects correctly.
    """
    i = {'type': 'object', 'properties': {'this is a': {'type': 'string', 'example': 'test'}}}
    assert base._iterate_schema_dict(i) == {'this is a': 'test'}

    i = {
        'type': 'object',
        'properties': {'this is a': {'type': 'array', 'items': {'type': 'string', 'example': 'test'}}},
    }
    assert base._iterate_schema_dict(i) == {'this is a': ['test']}

    i = {
        'type': 'object',
        'properties': {'this is a': {'type': 'object', 'properties': {'nested': {'type': 'string', 'example': 'dict'}}}},
    }
    assert base._iterate_schema_dict(i) == {'this is a': {'nested': 'dict'}}

    base._iterate_schema_dict({'type': 'string', 'properties': {'string without example': {'type': 'string'}}})
    assert "Item `{'type': 'string'}` is missing an explicit example value" == caplog.records[-1].message


def test_iterate_schema_list(caplog):
    """
    Tests that we're parsing schema arrays correctly.
    """
    assert base._iterate_schema_list({'type': 'array', 'items': {'type': 'string', 'example': 'test'}}) == ['test']

    i = {'type': 'array', 'items': {'type': 'array', 'items': {'type': 'string', 'example': 'test'}}}
    assert base._iterate_schema_list(i) == [['test']]

    i = {
        'type': 'array',
        'items': {'type': 'object', 'properties': {'this is a': {'type': 'string', 'example': 'test'}}},
    }
    assert base._iterate_schema_list(i) == [{'this is a': 'test'}]

    base._iterate_schema_list({'type': 'array', 'items': {'type': 'string'}})
    assert "Item `{'type': 'string'}` is missing an explicit example value" == caplog.records[-1].message


def test_failed_creation(monkeypatch):
    with pytest.raises(
        ImproperlyConfigured, match="Not able to construct an example from schema {'type': 'array', 'items': False}"
    ):
        _LoaderBase().create_dict_from_schema({'type': 'array', 'items': False})


def test_item_without_example(monkeypatch):
    for item, expected in [
        (deepcopy(string_type), 'string'),
        (deepcopy(integer_type), 1),
        (deepcopy(number_type), 1.0),
        (deepcopy(bool_type), True),
    ]:
        del item['example']
        assert _LoaderBase().create_dict_from_schema(item) == expected
