from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView


class Products(APIView):
    def get(self, request: Request, version: int, category_pk: int, subcategory_pk: int) -> Response:
        products = {
            1: {
                1: {},
                2: {},
                3: {}
            },
            2: {
                1: {},
                2: {},
                3: {}
            },
            3: {
                1: {},
                2: {},
                3: {}
            },
            4: {
                1: {},
                2: {},
                3: {}
            }
        }
        return Response(products.get(category_pk, {}).get(subcategory_pk, {}), HTTP_200_OK)
