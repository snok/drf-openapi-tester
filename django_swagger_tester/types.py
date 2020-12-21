from typing import Union

from django_swagger_tester.loaders import DrfSpectacularSchemaLoader, DrfYasgSchemaLoader, StaticSchemaLoader

LoaderClass = Union[DrfSpectacularSchemaLoader, DrfYasgSchemaLoader, StaticSchemaLoader]
