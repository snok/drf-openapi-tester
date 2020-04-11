import pytest
import yaml
from django.conf import settings

from django_swagger_tester.case.base import ResponseSchemaCaseTester
from django_swagger_tester.exceptions import CaseError
from django_swagger_tester.utils import replace_refs


def load_schema(path):
    with open(settings.BASE_DIR + path, 'r') as f:
        return replace_refs(yaml.load(f, Loader=yaml.FullLoader))


schema = load_schema('/tests/drf_yasg_reference.yaml')


def test_schema_case_tester_on_reference_schema():
    """
    Runs schema test class on reference schema.

    The iteration is done to test all paths, status codes, and responses.
    """
    for key in schema['paths'].keys():
        for method in schema['paths'][key].keys():
            if 'responses' not in schema['paths'][key][method]:
                continue
            for status_code in schema['paths'][key][method]['responses'].keys():
                if 'schema' not in schema['paths'][key][method]['responses']:
                    continue
                with pytest.raises(CaseError, match='The property `date_created` is not properly camelCased'):
                    ResponseSchemaCaseTester(
                        schema=schema['paths'][key][method]['responses'][status_code]['schema'], key=f'path: {key}\nmethod: {method}'
                    )


def test_ignore_case():
    for key in schema['paths'].keys():
        for method in schema['paths'][key].keys():
            if 'responses' not in schema['paths'][key][method]:
                continue
            for status_code in schema['paths'][key][method]['responses'].keys():
                if 'schema' not in schema['paths'][key][method]['responses']:
                    continue
                with pytest.raises(CaseError, match='The property `read_only_nullable` is not properly camelCased'):
                    ResponseSchemaCaseTester(schema=schema['paths'][key][method]['responses'][status_code]['schema'],
                                             key=f'path: {key}\nmethod: {method}', ignore_case=['date_created', 'date_modified'])


class MockSettings:
    CASE = 'snake_case'


def test_schema_using_snake_case(monkeypatch):
    monkeypatch.setattr('django_swagger_tester.case.base.settings', MockSettings)
    for key in schema['paths'].keys():
        for method in schema['paths'][key].keys():
            if 'responses' not in schema['paths'][key][method]:
                continue
            for status_code in schema['paths'][key][method]['responses'].keys():
                if 'schema' not in schema['paths'][key][method]['responses']:
                    continue
                ResponseSchemaCaseTester(schema=schema['paths'][key][method]['responses'][status_code]['schema'])
