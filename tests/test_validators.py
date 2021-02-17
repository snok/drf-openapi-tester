import base64
from typing import Any, Dict, Tuple

import pytest
from faker import Faker

from openapi_tester.validators import VALIDATOR_MAP

faker = Faker()

TEST_DATA_MAP: Dict[str, Tuple[Any, Any]] = {
    # by type
    "string": (faker.pystr(), faker.pyint()),
    "file": (faker.pystr(), faker.pyint()),
    "boolean": (faker.pybool(), faker.pystr()),
    "integer": (faker.pyint(), faker.pyfloat()),
    "number": (faker.pyfloat(), faker.pybool()),
    "object": (faker.pydict(), faker.pystr()),
    "array": (faker.pylist(), faker.pystr()),
    # by format
    "byte": (base64.b64encode(faker.pystr().encode("utf-8")).decode("utf-8"), faker.pystr(min_chars=5, max_chars=5)),
    "base64": (base64.b64encode(faker.pystr().encode("utf-8")).decode("utf-8"), faker.pystr(min_chars=5, max_chars=5)),
    "date": (faker.date(), faker.pystr()),
    "date-time": (faker.date_time().isoformat(), faker.pystr()),
    "double": (faker.pyfloat(), faker.pyint()),
    "email": (faker.email(), faker.pystr()),
    "float": (faker.pyfloat(), faker.pyint()),
    "ipv4": (faker.ipv4(), faker.pystr()),
    "ipv6": (faker.ipv6(), faker.pystr()),
    "time": (faker.time(), faker.pystr()),
    "uri": (faker.url(), faker.pystr()),
    "url": (faker.url(), faker.pystr()),
    "uuid": (faker.uuid4(), faker.pystr()),
}


@pytest.mark.parametrize("label", VALIDATOR_MAP.keys())
def test_validator(label: str):
    validator = VALIDATOR_MAP[label]
    good_data, bad_data = TEST_DATA_MAP[label]
    assert validator(good_data) is True
    assert validator(bad_data) is False
