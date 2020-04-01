from typing import List

from django.conf import settings
from django.urls import URLPattern


def list_project_urls() -> List[str]:
    """
    Returns a list of the Django projects URLs.
    """
    urlconf = __import__(settings.ROOT_URLCONF, {}, {}, [''])

    def list_urls(urls, acc=None):  # noqa: TYP201, TYP001
        if acc is None:
            acc = []
        if not urls:
            return
        url = urls[0]
        if isinstance(url, URLPattern):
            yield acc + [str(url.pattern)]
        # elif isinstance(url, URLResolver):
        #     yield from list_urls(url.url_patterns, acc + [str(url.pattern)])
        yield from list_urls(urls[1:], acc)

    return [''.join(p) for p in list_urls(urlconf.urlpatterns) if ''.join(p)]
