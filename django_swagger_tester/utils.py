import logging
import re
from typing import List

from rest_framework.schemas.generators import EndpointEnumerator

logger = logging.getLogger('django_swagger_tester')


def get_paths() -> List[str]:
    """
    Returns a list of endpoint paths.
    """
    return list(set(endpoint[0] for endpoint in EndpointEnumerator().get_api_endpoints()))  # noqa: C401


def convert_resolved_url(resolved_url: str) -> str:
    """
    Converts an url:

        - from /api/v1/<vehicle_type:vehicle_type>/ to /api/v1/{vehicle_type}/, and
        - from /api/v1/<vehicle_type>/ to /api/v1/{vehicle_type}/

    :return: Converted url
    """
    patterns = [
        {
            'pattern': r'<\w+:\w+>',
            'string_pattern': '<{keyword}:{keyword}>',
            'first_index': '<',
            'second_index': ':'
        },
        {
            'pattern': r'<\w+>',
            'string_pattern': '<{keyword}>',
            'first_index': '<',
            'second_index': '>'
        }]

    for item in patterns:
        matches = re.findall(item['pattern'], resolved_url)
        if matches:
            url = resolved_url
            for dynamic_url in matches:
                keyword = dynamic_url[dynamic_url.index(item['first_index']) + 1: dynamic_url.index(item['second_index'])]
                url = url.replace(item['string_pattern'].format(keyword=keyword), f'{{{keyword}}}')
            logger.debug('Converted resolved url from `%s` to `%s`', resolved_url, url)
            resolved_url = url
    return resolved_url
