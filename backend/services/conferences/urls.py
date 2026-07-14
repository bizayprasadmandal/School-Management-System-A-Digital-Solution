"""Conference Scheduler URL Configuration."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConferenceSlotViewSet

app_name = "conferences"

router = DefaultRouter()
router.register(r"conference-slots", ConferenceSlotViewSet, basename="conference_slot")

urlpatterns = [
    path("", include(router.urls)),
]
