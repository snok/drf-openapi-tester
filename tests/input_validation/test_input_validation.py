from demo_project.api.swagger.auto_schemas import VehicleSerializer

s = VehicleSerializer
field_keys = [key for key in s.fields]

data = {
  'vehicleType': 'truck'
}

"""
Required function inputs:
- Serializer
- Input body

Input body can be fetched


"""

from rest_framework import status

# Run validation
# Check key cases
