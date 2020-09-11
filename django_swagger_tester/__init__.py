import django_swagger_tester.testing as drf_yasg  # here for backwards compatibility from v1
import django_swagger_tester.testing as static  # here for backwards compatibility from v1

default_app_config = 'django_swagger_tester.apps.DjangoSwaggerTesterConfig'

__version__ = '2.0.0'  # Remember to also change pyproject.toml version
__author__ = 'Sondre Lillebø Gundersen'
__all__ = ['testing', 'case_testers', 'loaders', 'exceptions']
