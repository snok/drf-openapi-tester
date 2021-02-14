import pytest
from django.core.exceptions import ImproperlyConfigured

from openapi_tester import DrfSpectacularSchemaLoader, DrfYasgSchemaLoader, SchemaTester, StaticSchemaLoader
from openapi_tester.constants import INIT_ERROR


def test_loader_inference(settings):
    # Test drf-spectacular
    assert isinstance(SchemaTester().loader, DrfSpectacularSchemaLoader)

    # Test drf-yasg
    settings.INSTALLED_APPS.pop(settings.INSTALLED_APPS.index("drf_spectacular"))
    settings.INSTALLED_APPS.append("drf_yasg")
    assert isinstance(SchemaTester().loader, DrfYasgSchemaLoader)

    # Test static loader
    assert isinstance(SchemaTester(schema_file_path="test").loader, StaticSchemaLoader)

    # Test no loader
    settings.INSTALLED_APPS = []
    with pytest.raises(ImproperlyConfigured, match=INIT_ERROR):
        SchemaTester()
