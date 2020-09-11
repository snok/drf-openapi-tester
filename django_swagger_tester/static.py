# File is only here for backward compatibility from v1. Remove by v3.
# If you delete this file, make sure to also remove drf_yasg.py
from warnings import warn

warn(
    'Importing validate_response from django_swagger_tester.static is deprecated as of version 2. '
    'Replace it with `django_swagger_tester.testing`.'
)

from django_swagger_tester.testing import validate_response  # noqa: F401, E402
