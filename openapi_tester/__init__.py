from .tester import OpenAPITester
from .config import Settings

settings = Settings()
validate_schema = OpenAPITester(settings.path, settings.case).validate_schema
