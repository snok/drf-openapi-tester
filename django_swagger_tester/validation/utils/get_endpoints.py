import logging
from typing import List

logger = logging.getLogger('django_swagger_tester')


def get_endpoint_paths() -> List[str]:
    """
    Returns a list of endpoint paths.
    """
    from rest_framework.schemas.generators import EndpointEnumerator

    return list({endpoint[0] for endpoint in EndpointEnumerator().get_api_endpoints()})
