from typing import Any, List, Optional

from openapi_tester.constants import OPENAPI_PYTHON_MAPPING


class SchemaToPythonConverter:
    """ This class is used both by the DocumentationError format method and the various test suites """

    def __init__(self, schema: dict, with_faker: bool = False):
        if 'allOf' in schema:
            from openapi_tester.schema_tester import SchemaTester

            merged_schema = SchemaTester.handle_all_of(**schema)
            schema = merged_schema
        if with_faker:
            """ We are importing faker here to ensure this remains a dev dependency """
            from faker import Faker

            Faker.seed(0)
            self.faker = Faker()
        schema_type = schema.get('type')
        if not schema_type and 'properties' in schema:
            schema_type = 'object'

        if schema_type == 'array':
            self.result = self._iterate_schema_list(schema)  # type :ignore
        elif schema_type == 'object':
            self.result = self._iterate_schema_dict(schema)  # type :ignore
        else:
            self.result = self._to_mock_value(schema_type, schema.get('enum'))  # type :ignore

    def _to_mock_value(self, schema_type: Any, enum: Optional[List[Any]]) -> Any:
        if enum:
            return enum[0]
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
        if 'allOf' in schema_object:
            from openapi_tester.schema_tester import SchemaTester

            schema_object = SchemaTester.handle_all_of(**schema_object)
        if 'properties' in schema_object:
            properties = schema_object['properties']
        elif 'additionalProperties' in schema_object:
            properties = {'': schema_object['additionalProperties']}
        else:
            # TODO: (Q) should this be handled better?
            properties = {}

        for key, value in properties.items():
            if 'example' in value:
                parsed_schema[key] = value['example']
            elif 'anyOf' in value:
                value = value['anyOf'][0]
            elif 'oneOf' in value:
                value = value['oneOf'][0]
            value_type = value.get('type')
            if not value_type and 'properties' in value:
                value_type = 'object'
            elif not value_type:
                continue
            if value_type == 'object':
                parsed_schema[key] = self._iterate_schema_dict(value)
            elif value_type == 'array':
                parsed_schema[key] = self._iterate_schema_list(value)  # type: ignore
            else:
                parsed_schema[key] = self._to_mock_value(value['type'], value.get('enum'))
        return parsed_schema

    def _iterate_schema_list(self, schema_array: Any) -> Any:
        parsed_items = []
        raw_items = schema_array['items']
        if 'allOf' in raw_items.keys():
            from openapi_tester.schema_tester import SchemaTester

            raw_items = SchemaTester.handle_all_of(**raw_items)
        items_type = raw_items.get('type')
        if not items_type and 'properties' in raw_items:
            items_type = 'object'
        elif not items_type:
            return []
        if items_type == 'object':
            parsed_items.append(self._iterate_schema_dict(raw_items))  # type :ignore
        elif items_type == 'array':
            parsed_items.append(self._iterate_schema_list(raw_items))  # type :ignore
        else:
            parsed_items.append(self._to_mock_value(items_type, raw_items.get('enum')))  # type :ignore
        return parsed_items
