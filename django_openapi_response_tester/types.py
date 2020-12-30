from typing import Union

from django_openapi_response_tester.loaders import DrfSpectacularSchemaLoader, DrfYasgSchemaLoader, StaticSchemaLoader

LoaderClass = Union[DrfSpectacularSchemaLoader, DrfYasgSchemaLoader, StaticSchemaLoader]
