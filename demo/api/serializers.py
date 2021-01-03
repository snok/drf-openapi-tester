from rest_framework import serializers


class VehicleSerializer(serializers.Serializer):
    class Meta:
        swagger_schema_fields = {'example': {'vehicleType': 'truck'}}

    vehicle_type = serializers.CharField(max_length=10)


class ItemSerializer(serializers.Serializer):
    item_type = serializers.CharField(max_length=10)


class CarSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=254)
    color = serializers.CharField(max_length=254)
    height = serializers.CharField(max_length=254)
    width = serializers.CharField(max_length=254)
    length = serializers.CharField(max_length=254)
