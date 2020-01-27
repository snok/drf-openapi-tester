from openapi_tester.case import skip


def test_skip():
    for item in [1, '2', 's', 2.2, [], {}, (1,), None]:
        assert skip(item) is None
