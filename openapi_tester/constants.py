import re

OPENAPI_PYTHON_MAPPING = {
    "boolean": bool.__name__,
    "string": str.__name__,
    "file": str.__name__,
    "array": list.__name__,
    "object": dict.__name__,
    "integer": int.__name__,
    "number": f"{int.__name__} or {float.__name__}",
}
PARAMETER_CAPTURE_REGEX = re.compile(r"({[\w]+})")
