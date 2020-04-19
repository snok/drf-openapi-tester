import logging
from typing import Any

from django_swagger_tester.case.checks import case_check
from django_swagger_tester.case.utils import conditional_check, set_ignored_keys
from django_swagger_tester.configuration import settings
from django_swagger_tester.openapi import read_items, read_properties, read_type

logger = logging.getLogger('django_swagger_tester')


class ResponseCaseTester(object):
    """
    Iterates through an API response objects to verify that dict keys are cased correctly.
    The case we're checking for depends on the projects SWAGGER_TESTER `CASE` setting.
    """

    def __init__(self, response_data: Any, **kwargs) -> None:
        """
        Finds the appropriate case check function and calls the appropriate function base on the response datas type.

        :param response_data: typically will be an API responses response.json() output.
        """
        self.case_check = case_check(settings.CASE)
        self.ignored_keys = set_ignored_keys(**kwargs)
        if isinstance(response_data, dict):
            self.test_dict(response_data)
        elif isinstance(response_data, list):
            self.test_list(response_data)
        else:
            logger.debug('Skipping case check')

    def test_dict(self, dictionary: dict) -> None:
        """
        Iterates through a response dictionary to check keys' case, and to pass nested values for further test_checks.
        """
        if not isinstance(dictionary, dict):
            raise ValueError(f'Expected dictionary, but received {type(dictionary)}')
        for key, value in dictionary.items():
            conditional_check(key, self.case_check, self.ignored_keys)
            if isinstance(value, dict):
                self.test_dict(dictionary=value)
            elif isinstance(value, list):
                self.test_list(items=value)

    def test_list(self, items: list) -> None:
        """
        Iterates through a response list to pass appropriate nested items for further test_checks.
        Only dictionary keys need case checking, so that's what we're looking for.

        :param items: list of unknown items
        """
        if not isinstance(items, list):
            raise ValueError(f'Expected list, but received {type(items)}')
        for item in items:
            if isinstance(item, dict):
                self.test_dict(dictionary=item)
            elif isinstance(item, list):
                self.test_list(items=item)


class SchemaCaseTester(object):
    """
    Iterates through an OpenAPI schema to verify that object keys are cased correctly.
    The case we're checking for depends on the projects SWAGGER_TESTER `CASE` setting.
    """

    def __init__(self, schema: dict, **kwargs) -> None:
        """
        Finds the appropriate case check function and calls the appropriate function base on the schema item type.

        :param schema: openapi schema item
        """
        self.case_check = case_check(settings.CASE)
        self.ignored_keys = set_ignored_keys(**kwargs)
        if read_type(schema) == 'object':
            logger.debug('root -> dict')
            self.test_dict(schema)
        elif read_type(schema) == 'array':
            logger.debug('root -> list')
            self.test_list(schema)
        else:
            logger.debug('Skipping case check')

    def test_dict(self, obj: dict) -> None:
        """
        Iterates through a schema object to check keys' case, and to pass nested values for further test_checks.
        """
        properties = read_properties(obj)
        for key, value in properties.items():
            conditional_check(key, self.case_check, self.ignored_keys)
            if read_type(value) == 'object':
                logger.debug('dict -> dict')
                self.test_dict(obj=value)
            elif read_type(value) == 'array':
                logger.debug('dict -> list')
                self.test_list(array=value)

    def test_list(self, array: dict) -> None:
        """
        Iterates through a schema array to pass appropriate nested items for further test_checks.
        Only object keys need case checking, so that's what we're looking for.
        """
        item = read_items(array)
        if read_type(item) == 'object':
            logger.debug('list -> dict')
            self.test_dict(obj=item)
        elif read_type(item) == 'array':
            logger.debug('list -> list')
            self.test_list(array=item)
