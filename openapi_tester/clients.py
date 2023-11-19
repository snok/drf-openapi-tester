"""Subclass of ``APIClient`` using ``SchemaTester`` to validate responses."""
from __future__ import annotations

from typing import TYPE_CHECKING

from rest_framework.test import APIClient

from .schema_tester import SchemaTester

if TYPE_CHECKING:
    from rest_framework.response import Response


class OpenAPIClient(APIClient):
    """``APIClient`` validating responses against OpenAPI schema."""

    def __init__(
        self,
        *args,
        schema_tester: SchemaTester | None = None,
        **kwargs,
    ) -> None:
        """Initialize ``OpenAPIClient`` instance."""
        super().__init__(*args, **kwargs)
        self.schema_tester = schema_tester or self._schema_tester_factory()

    def request(self, **kwargs) -> Response:  # type: ignore[override]
        """Validate fetched response against given OpenAPI schema."""
        response = super().request(**kwargs)
        if self._is_successful_response(response):
            self.schema_tester.validate_request(response)
        self.schema_tester.validate_response(response)
        return response

    @staticmethod
    def _is_successful_response(response: Response) -> bool:
        return response.status_code < 400

    @staticmethod
    def _schema_tester_factory() -> SchemaTester:
        """Factory of default ``SchemaTester`` instances."""
        return SchemaTester()
