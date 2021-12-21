from __future__ import annotations

from typing import TYPE_CHECKING

from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView

if TYPE_CHECKING:
    from rest_framework.request import Request


class Products(APIView):
    def get(self, request: Request, version: int, category_pk: int, subcategory_pk: int) -> Response:
        products: dict[int, dict] = {
            1: {1: {}, 2: {}, 3: {}},
            2: {1: {}, 2: {}, 3: {}},
            3: {1: {}, 2: {}, 3: {}},
            4: {1: {}, 2: {}, 3: {}},
        }
        return Response(products.get(category_pk, {}).get(subcategory_pk, {}), HTTP_200_OK)
