from __future__ import annotations

from typing import TYPE_CHECKING

from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView

from test_project.api.serializers import PetsSerializer

if TYPE_CHECKING:
    from rest_framework.request import Request


class Pet(APIView):
    def get(self, request: Request, petId: int) -> Response:
        pet = {"name": "doggie", "category": {"id": 1, "name": "Dogs"}, "photoUrls": [], "status": "available"}
        return Response(pet, HTTP_200_OK)

    def post(self, request) -> Response:
        serializer = PetsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"id": 1, "name": request.data["name"]}, 201)
