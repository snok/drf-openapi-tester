import pkg_resources

from openapi_tester.tester import validate_schema  # noqa: F401

__version__ = pkg_resources.get_distribution('openapi-tester').version
__all__ = ['validate_schema']
