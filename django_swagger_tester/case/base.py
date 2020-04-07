import logging
from typing import List

from django_swagger_tester.case.checks import case_check
from django_swagger_tester.configuration import settings

logger = logging.getLogger('django_swagger_tester')


# noinspection PyMethodMayBeStatic
class ResponseCaseTester(object):

    def __init__(self, response_data, **kwargs) -> None:
        self.case_func = case_check(settings.CASE)
        self.ignored_keys = self.set_ignored_keys(**kwargs)
        if isinstance(response_data, dict):
            self.dict(response_data)
        elif isinstance(response_data, list):
            self.list(response_data)
        else:
            logger.debug('Skipping case check')

    def set_ignored_keys(self, **kwargs) -> List[str]:
        """
        Lets users pass a list of string that will not be checked by case-check.
        For example, validate_response(..., ignore_case=["List", "OF", "improperly cased", "kEYS"]).
        """
        if 'ignore_case' in kwargs:
            return kwargs['ignore_case']
        return []

    def dict(self, dictionary: dict) -> None:
        if not isinstance(dictionary, dict):
            raise ValueError(f'Expected dictonary, but received {dictionary}')
        for key in dictionary.keys():
            value = dictionary[key]
            if key not in self.ignored_keys:
                self.case_func(key)
            else:
                logger.debug('Skipping case check for key `%s`', key)
            if isinstance(value, dict):
                self.dict(dictionary=value['properties'])
            elif isinstance(value, list):
                self.list(list_items=value)

    def list(self, list_items: list) -> None:
        if not isinstance(list_items, list):
            raise ValueError(f'Expected list, but received {list_items}')
        for item in list_items:
            if isinstance(item, dict):
                self.dict(dictionary=item)
            elif isinstance(item, list):
                self.list(list_items=item)


class ResponseSchemaCaseTester(object):

    def __init__(self, schema, **kwargs) -> None:
        self.case_func = case_check(settings.CASE)
        self.ignored_keys = self.set_ignored_keys(**kwargs)
        if schema['type'] == 'object':
            logger.debug('Dict from root')
            self.dict(schema)
        elif schema['type'] == 'array':
            logger.debug('List from root')
            self.list(schema)
        else:
            logger.debug('Skipping case check')

    def set_ignored_keys(self, **kwargs) -> List[str]:
        """
        Lets users pass a list of string that will not be checked by case-check.
        For example, validate_response(..., ignore_case=["List", "OF", "improperly cased", "kEYS"]).
        """
        if 'ignore_case' in kwargs:
            return kwargs['ignore_case']
        return []

    def dict(self, dictionary: dict) -> None:
        if 'properties' not in dictionary:
            logger.warning('properties missing from %s', dictionary)
            return
        for key in dictionary['properties'].keys():
            value = dictionary['properties'][key]
            if key not in self.ignored_keys:
                self.case_func(key)
            else:
                logger.debug('Skipping case check for key `%s`', key)

            if not (isinstance(value, dict) and 'type' in value):
                logger.warning('%s is not a dict or is missing type', value)
                return
            if value['type'] == 'object':
                logger.debug('Dict from dict')
                self.dict(dictionary=value)
            elif value['type'] == 'array':
                logger.debug('List from dict')
                self.list(list_items=value)

    def list(self, list_items: dict) -> None:
        for item in list_items['items']:
            if not (isinstance(item, dict) and 'type' in item):
                logger.warning('%s is not a dict or is missing type', item)
                return
            if item['type'] == 'object':
                logger.debug('Dict from list')
                self.dict(dictionary=item)
            elif item['type'] == 'array':
                logger.debug('List from list')
                self.list(list_items=item)
