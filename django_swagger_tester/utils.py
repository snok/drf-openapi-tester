from typing import List

from django.conf import settings
from django.urls import URLPattern, URLResolver


def list_project_urls() -> List[str]:
    """
    Returns a list of the Django projects URLs.
    """
    urlconf = __import__(settings.ROOT_URLCONF, {}, {}, [''])

    def list_urls(lis, acc=None):
        if acc is None:
            acc = []
        if not lis:
            return
        l = lis[0]
        if isinstance(l, URLPattern):
            yield acc + [str(l.pattern)]
        elif isinstance(l, URLResolver):
            yield from list_urls(l.url_patterns, acc + [str(l.pattern)])
        yield from list_urls(lis[1:], acc)

    return [''.join(p) for p in list_urls(urlconf.urlpatterns)]
