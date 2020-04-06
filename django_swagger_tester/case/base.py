import logging
from typing import List

from django_swagger_tester.case.checks import case_check
from django_swagger_tester.configuration import settings

logger = logging.getLogger('django_swagger_tester')


# noinspection PyMethodMayBeStatic
class CaseTester(object):

    def __init__(self, **kwargs) -> None:
        self.case_func = case_check(settings.CASE)
        self.ignored_keys = self.set_ignored_keys(**kwargs)

    def set_ignored_keys(self, **kwargs) -> List[str]:
        """
        Lets users pass a list of string that will not be checked by case-check.
        For example, validate_response(..., ignore_case=["List", "OF", "improperly cased", "kEYS"]).
        """
        if 'ignore_case' in kwargs:
            return kwargs['ignore_case']
        return []

    def dict(self, dictionary: dict) -> None:
        """
        Verifies that a dictionary contains keys of the right case-type.

        :param dictionary: dict
        :raises: django_swagger_tester.exceptions.CaseError
        """
        logger.debug('Checking dictionary casing')

        if not isinstance(dictionary, dict):
            raise ValueError(f'Expected dictonary, but received {dictionary}')

        for key in dictionary.keys():

            # Check the keys for case inconsistencies
            if key not in self.ignored_keys:
                self.case_func(key)
            else:
                logger.debug('Skipping case check for key `%s`', key)

            # Pass nested elements for nested checks
            value = dictionary[key]

            if value['type'] == 'object':
                logger.debug('Calling _dict from _dict. Value: %s', value)
                self.dict(dictionary=value['properties'])
            elif value['type'] == 'array':
                logger.debug('Calling _list from _dict. Value: %s', value)
                self.list(list_items=value)

    def list(self, list_items: list) -> None:
        """
        Verifies that a list contains keys of the right case-type.

        :param list_items: list
        :raises: django_swagger_tester.exceptions.CaseError
        """
        logger.debug('Verifying that response list layer matches schema layer')
        if not isinstance(list_items, list):
            raise ValueError(f'Expected list, but received {list_items}')

        for item in list_items:

            # List item --> dict
            if item['type'] == 'object' and item['properties']:
                logger.debug('Calling _dict from _list')
                self.dict(dictionary=item['properties'])

            # List item --> list
            elif item['type'] == 'array' and item['items']:
                logger.debug('Calling _list from _list')
                self.list(list_items=item)
