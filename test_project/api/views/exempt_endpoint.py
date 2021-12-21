from __future__ import annotations

from typing import TYPE_CHECKING

from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.views import APIView

if TYPE_CHECKING:
    from rest_framework.request import Request


class Exempt(APIView):
    def get(self, request: Request, version: int) -> Response:
        return Response(status=HTTP_204_NO_CONTENT)
