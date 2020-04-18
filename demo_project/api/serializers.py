from rest_framework import serializers


class VehicleSerializer(serializers.Serializer):
    class Meta:
        swagger_schema_fields = {'example': {'vehicleType': 'truck'}}

    vehicle_type = serializers.CharField(max_length=10)
