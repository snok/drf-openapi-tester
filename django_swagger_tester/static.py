# File is only here for backward compatibility from v1. Remove by v3.
# If you delete this file, make sure to also remove drf_yasg.py
from warnings import warn

warn(
    'Importing from django_swagger_tester.static was deprecated in version 2. '
    'Replace it with `from django_swagger_tester.testing`.'
)

from django_swagger_tester.testing import validate_response  # noqa: F401, E402
from django_swagger_tester.testing import validate_input_serializer as validate_input  # noqa: F401, E402
