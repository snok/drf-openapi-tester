# import pytest
# import yaml
# from django.core.exceptions import ImproperlyConfigured
#
# from demo_project import settings
# from django_swagger_tester.configuration import settings as _settings
#
#
# def loader(path):
#     with open(settings.BASE_DIR + path, 'r') as f:
#         return _settings.LOADER_CLASS.replace_refs(yaml.load(f, Loader=yaml.FullLoader))
#
#
# schema = loader('/tests/drf_yasg_reference.yaml')
#
#
# def test_create_dict_from_schema():
#     """
#     Makes sure we're able to accurately serialize an object.
#     """
#     e = (
#         'This schema item does not seem to have an example value. '
#         "Item: {'description': 'title model help_text', 'type': 'string', 'maxLength': 255, 'minLength': 1}"
#     )
#     with pytest.raises(ImproperlyConfigured, match=e):
#         for key in schema['paths'].keys():
#             for method in schema['paths'][key].keys():
#                 if 'responses' not in schema['paths'][key][method]:
#                     continue
#                 for status_code in schema['paths'][key][method]['responses'].keys():
#                     if 'schema' not in schema['paths'][key][method]['responses'][status_code]:
#                         continue
#                     try:
#                         response_schema = _settings.LOADER_CLASS.get_request_body_schema_section(schema['paths'][key][method]['parameters'])
#                     except ImproperlyConfigured:
#                         continue
#                     _settings.LOADER_CLASS.create_dict_from_schema(response_schema)
#
#
# def test_iterate_schema_dict():
#     """
#     Tests that we're parsing schema objects correctly.
#     """
#     i = {'type': 'object', 'properties': {'this is a': {'type': 'string', 'example': 'test'}}}
#     assert _iterate_schema_dict(i) == {'this is a': 'test'}
#
#     i = {
#         'type': 'object',
#         'properties': {'this is a': {'type': 'array', 'items': {'type': 'string', 'example': 'test'}}},
#     }
#     assert _iterate_schema_dict(i) == {'this is a': ['test']}
#
#     i = {
#         'type': 'object',
#         'properties': {
#             'this is a': {'type': 'object', 'properties': {'nested': {'type': 'string', 'example': 'dict'}}}
#         },
#     }
#     assert _iterate_schema_dict(i) == {'this is a': {'nested': 'dict'}}
#
#     with pytest.raises(ImproperlyConfigured):
#         _iterate_schema_dict({'type': 'string', 'properties': {'string without example': {'type': 'string'}}})
#
#
# def test_iterate_schema_list():
#     """
#     Tests that we're parsing schema arrays correctly.
#     """
#     assert _iterate_schema_list({'type': 'array', 'items': {'type': 'string', 'example': 'test'}}) == ['test']
#
#     i = {'type': 'array', 'items': {'type': 'array', 'items': {'type': 'string', 'example': 'test'}}}
#     assert _iterate_schema_list(i) == [['test']]
#
#     i = {
#         'type': 'array',
#         'items': {'type': 'object', 'properties': {'this is a': {'type': 'string', 'example': 'test'}}},
#     }
#     assert _iterate_schema_list(i) == [{'this is a': 'test'}]
#
#     with pytest.raises(ImproperlyConfigured):
#         _iterate_schema_list({'type': 'array', 'items': {'type': 'string'}})
