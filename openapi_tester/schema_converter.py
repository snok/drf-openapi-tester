from typing import Any

from openapi_tester.constants import OPENAPI_PYTHON_MAPPING


class SchemaToPythonConverter:
    """ This class is used both by the DocumentationError format method and the various test suites """

    def __init__(self, schema: dict, with_faker: bool = False):
        if with_faker:
            """ We are importing faker here to ensure this remains a dev dependency """
            from faker import Faker

            Faker.seed(0)
            self.faker = Faker()
        schema_type = schema['type']
        if schema_type == 'array':
            self.result = self._iterate_schema_list(schema)  # type :ignore
        elif schema_type == 'object':
            self.result = self._iterate_schema_dict(schema)  # type :ignore
        else:
            self.result = self._to_mock_value(schema_type)  # type :ignore

    def _to_mock_value(self, schema_type: Any) -> Any:
        if hasattr(self, 'faker'):
            faker_handlers = {
                'boolean': self.faker.pybool,
                'string': self.faker.pystr,
                'file': self.faker.pystr,
                'array': self.faker.pylist,
                'object': self.faker.pydict,
                'integer': self.faker.pyint,
                'number': self.faker.pyfloat,
            }
            return faker_handlers[schema_type]()
        else:
            return OPENAPI_PYTHON_MAPPING[schema_type]

    def _iterate_schema_dict(self, schema_object: Any) -> Any:
        parsed_schema = {}
        if 'properties' in schema_object:
            properties = schema_object['properties']
        elif 'additionalProperties' in schema_object:
            properties = {'': schema_object['additionalProperties']}
        elif 'allOf' in schema_object:
            from openapi_tester.schema_tester import SchemaTester

            properties = SchemaTester._merge_all_of(schema_object)
        for key, value in properties.items():
            value_type = value['type']
            if 'example' in value:
                parsed_schema[key] = value['example']
            elif value_type == 'object':
                parsed_schema[key] = self._iterate_schema_dict(value)
            elif value_type == 'array':
                parsed_schema[key] = self._iterate_schema_list(value)  # type: ignore
            else:
                parsed_schema[key] = self._to_mock_value(value['type'])
        return parsed_schema

    def _iterate_schema_list(self, schema_array: Any) -> Any:
        parsed_items = []
        raw_items = schema_array['items']
        items_type = raw_items['type']
        if items_type == 'object':
            parsed_items.append(self._iterate_schema_dict(raw_items))  # type :ignore
        elif items_type == 'array':
            parsed_items.append(self._iterate_schema_list(raw_items))  # type :ignore
        else:
            parsed_items.append(self._to_mock_value(items_type))  # type :ignore
        return parsed_items
