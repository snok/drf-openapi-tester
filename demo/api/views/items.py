import uuid

from rest_framework.response import Response
from rest_framework.views import APIView

from demo.api.serializers import ItemSerializer
from demo.api.swagger.auto_schemas import post_item_auto_schema


class Items(APIView):
    @post_item_auto_schema()
    def post(self, request):
        serializer = ItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'success': {'id': uuid.uuid4(), 'itemType': serializer.data.get('item_type', '')}}, 201)
