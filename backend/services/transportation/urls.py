"""Transportation Management URL Configuration."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    VehicleViewSet, DriverViewSet, RouteViewSet, RouteStopViewSet,
    StudentRouteViewSet, VehicleMaintenanceViewSet,
)

app_name = "transport_v1"

router = DefaultRouter()
router.register(r"vehicles", VehicleViewSet, basename="vehicle")
router.register(r"drivers", DriverViewSet, basename="driver")
router.register(r"routes", RouteViewSet, basename="route")
router.register(r"route-stops", RouteStopViewSet, basename="route-stop")
router.register(r"student-routes", StudentRouteViewSet, basename="student-route")
router.register(r"maintenance", VehicleMaintenanceViewSet, basename="maintenance")

urlpatterns = [
    path("", include(router.urls)),
]
