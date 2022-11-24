from __future__ import annotations

from typing import TYPE_CHECKING

from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework_json_api.views import RelationshipView

if TYPE_CHECKING:
    from rest_framework.request import Request


    
class PetOwnerRelationshipView(RelationshipView):
    def post(self, request: Request, petId: int, relatedField: str) -> Response:
        return Response({}, HTTP_200_OK)