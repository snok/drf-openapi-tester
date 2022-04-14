"""Subclass of ``APIClient`` using ``SchemaTester`` to validate responses."""
from __future__ import annotations

from typing import TYPE_CHECKING

from rest_framework.test import APIClient

if TYPE_CHECKING:
    from rest_framework.response import Response

    from .schema_tester import SchemaTester


class OpenAPIClient(APIClient):
    """``APIClient`` validating responses against OpenAPI schema."""

    def __init__(self, *args, schema_tester: SchemaTester, **kwargs) -> None:
        """Initialize ``OpenAPIClient`` instance."""
        super().__init__(*args, **kwargs)
        self.schema_tester = schema_tester

    def request(self, **kwargs) -> Response:  # type: ignore[override]
        """Validate fetched response against given OpenAPI schema."""
        response = super().request(**kwargs)
        self.schema_tester.validate_response(response)
        return response
