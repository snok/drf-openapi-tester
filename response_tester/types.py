from typing import Union

from response_tester.loaders import DrfSpectacularSchemaLoader, DrfYasgSchemaLoader, StaticSchemaLoader

LoaderClass = Union[DrfSpectacularSchemaLoader, DrfYasgSchemaLoader, StaticSchemaLoader]
