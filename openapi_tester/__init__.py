import pkg_resources

__version__ = pkg_resources.get_distribution('openapi-tester').version

from openapi_tester.tester import validate_schema  # noqa: F401
