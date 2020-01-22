__version__ = '0.0.3'
__author__ = 'Sondre Lillebø Gundersen'

from .tester import OpenAPITester
from .config import Settings

settings = Settings()
validate_schema = OpenAPITester(settings.path, settings.case).validate_schema
