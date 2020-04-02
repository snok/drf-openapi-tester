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
    Converts an url from /api/v1/<vehicle_type:vehicle_type>/ to /api/v1/{vehicle_type}/
    """
    dynamic_urls = re.findall(r'\/<\w+:\w+>\/', resolved_url)
    if not dynamic_urls:
        return resolved_url
    else:
        url = resolved_url
        for dynamic_url in dynamic_urls:
            keyword = dynamic_url[dynamic_url.index('<') + 1: dynamic_url.index(':')]
            url = url.replace(f'<{keyword}:{keyword}>', f'{{{keyword}}}')
        logger.debug('Converted resolved url from `%s` to `%s`', resolved_url, url)
        return url
