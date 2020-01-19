# from openapi_tester import openapi_tester
#
#
# def test_import_errors():
#     """
#     Asserts that bad declaration inputs raise appropriate errors.
#     """
#     input_data = [
#         # Incorrect `type` should raise a ValueError
#         {
#             'type': 'bad_type',
#             'path': None,
#             'expected': ValueError,
#             'expected_name': 'ValueError',
#             'expected_message': 'The input variable `type` needs to be "dynamic" or "static".',
#         },
#         # Wrong type for `type` should raise a TypeError
#         {
#             'type': 1,
#             'path': None,
#             'expected': TypeError,
#             'expected_name': 'TypeError',
#             'expected_message': 'The input variable `type` should be a string.',
#         },
#         # ValueError should be raised when type is "static" and path isn't a string
#         {
#             'type': 'static',
#             'path': None,
#             'expected': ValueError,
#             'expected_name': 'ValueError',
#             'expected_message': 'Please specify a path to your OpenAPI spec yaml file.',
#         },
#     ]
#
#     for item in input_data:
#         try:
#
#             @openapi_tester(type=item['type'])
#             def bad_type():
#                 pass
#
#             bad_type()
#             raise Exception(f'This should have raised a {item["expected_name"]}')
#         except item['expected'] as e:
#             assert str(e) == item['expected_message']
