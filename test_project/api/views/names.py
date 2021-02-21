from rest_framework.generics import RetrieveAPIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.serializers import ModelSerializer

from test_project.models import Names


class NamesSerializer(ModelSerializer):
    class Meta:
        model = Names
        fields = "__all__"


class NamesRetrieveView(RetrieveAPIView):
    model = Names
    serializer_class = NamesSerializer
    queryset = Names.objects

    def get_object(self):
        return Names.objects.get(custom_id_field=int(self.kwargs["pk"]))


class NameViewSet(ReadOnlyModelViewSet):
    serializer_class = NamesSerializer
    queryset = Names.objects.all()
