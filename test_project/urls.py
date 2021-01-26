from django.conf.urls.i18n import i18n_patterns
from django.urls import path, register_converter
from django.urls.converters import StringConverter
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from test_project import views
from test_project.api.views.animals import Animals
from test_project.api.views.cars import BadCars, GoodCars
from test_project.api.views.exempt_endpoint import Exempt
from test_project.api.views.i18n import Languages
from test_project.api.views.items import Items
from test_project.api.views.snake_cased_response import SnakeCasedResponse
from test_project.api.views.trucks import BadTrucks, GoodTrucks
from test_project.api.views.vehicles import Vehicles


class IsValidVehicleType(StringConverter):
    def to_python(self, value: str) -> str:
        if value in ["cars", "2", 2]:
            return value
        raise ValueError


class IsValidVersion(StringConverter):
    def to_python(self, value: str) -> str:
        if value in ["v1"]:
            return value
        raise ValueError


register_converter(IsValidVehicleType, "vehicle_type")
register_converter(IsValidVersion, "version")

api_urlpatterns = [
    path("api/<version:version>/cars/correct", GoodCars.as_view()),
    path("api/<version:version>/cars/incorrect", BadCars.as_view()),
    path("api/<version:version>/trucks/correct", GoodTrucks.as_view()),
    path("api/<version:version>/trucks/incorrect", BadTrucks.as_view()),
    path("api/<version:version>/vehicles", Vehicles.as_view()),
    path("api/<version:version>/animals", Animals.as_view()),
    path("api/<version:version>/items", Items.as_view()),
    path("api/<version:version>/exempt-endpoint", Exempt.as_view()),
    path("api/<version:version>/snake-case/", SnakeCasedResponse.as_view()),
    # ^trailing slash is here on purpose
]

internationalised_urlpatterns = i18n_patterns(
    path("api/<version:version>/i18n", Languages.as_view()),
)


swagger_info = openapi.Info(
    title="DRF_YASG test project",
    default_version="v1",
    description="drf_yasg implementation for OpenAPI spec generation.",
    contact=openapi.Contact(email=""),
)
schema_view = get_schema_view(
    swagger_info,
    patterns=api_urlpatterns + internationalised_urlpatterns,
    public=False,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("", views.index),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]
urlpatterns += api_urlpatterns + internationalised_urlpatterns
