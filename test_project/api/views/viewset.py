from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import GenericViewSet

from test_project.models import Names


class NamesSerializer(ModelSerializer):
    class Meta:
        model = Names
        fields = "__all__"


class NamesApi(GenericViewSet):
    model = Names
    serializer_class = NamesSerializer
    queryset = Names.objects.all()

    def retrieve(self, request, version, id):
        return Response(status=204)
