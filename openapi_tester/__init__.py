__version__ = '0.0.3'
__author__ = 'Sondre Lillebø Gundersen'

from .tester import OpenAPITester

validate_schema = OpenAPITester().validate_schema
