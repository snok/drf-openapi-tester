from pathlib import Path

current_path = Path(__file__).resolve(strict=True).parent

yml_path = f'{current_path}/test_schemas/openapi-schema.yml'
yml_split_path = f'{current_path}/test_schemas/openapi-schema-split.yaml'
json_path = f'{current_path}/test_schemas/openapi-schema.json'
