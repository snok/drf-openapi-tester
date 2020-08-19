from django.urls import path, register_converter
from django.urls.converters import StringConverter
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from demo import views
from demo.api.views.cars import BadCars, GoodCars
from demo.api.views.items import Items
from demo.api.views.trucks import BadTrucks, GoodTrucks
from demo.api.views.vehicles import Vehicles


class IsValidVehicleType(StringConverter):
    def to_python(self, value: str) -> str:
        if value == 'cars':
            return value
        raise ValueError


register_converter(IsValidVehicleType, 'vehicle_type')

api_urlpatterns = [
    path('api/v1/<vehicle_type:vehicle_type>/correct/', GoodCars.as_view(), name='correctly_documented_cars'),
    path('api/v1/<vehicle_type:vehicle_type>/incorrect/', BadCars.as_view(), name='incorrectly_documented_cars'),
    path('api/v1/trucks/correct/', GoodTrucks.as_view(), name='correctly_documented_trucks'),
    path('api/v1/trucks/incorrect/', BadTrucks.as_view(), name='incorrectly_documented_trucks'),
    path('api/v1/vehicles/', Vehicles.as_view(), name='vehicles'),
    path('api/v1/items/', Items.as_view(), name='items'),
]

schema_view = get_schema_view(
    openapi.Info(
        title='DRF_YASG test project',
        default_version='v1',
        description='drf_yasg implementation for OpenAPI spec generation.',
        contact=openapi.Contact(email=''),
    ),
    url='http://127.0.0.1:8080',
    patterns=api_urlpatterns,
    public=False,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('', views.index),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
] + api_urlpatterns
