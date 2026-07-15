"""Conference Scheduler URL Configuration with Zoom integration."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConferenceSlotViewSet, ZoomConnectionView, ZoomMeetingsListView

app_name = "conferences"

router = DefaultRouter()
router.register(r"conference-slots", ConferenceSlotViewSet, basename="conference_slot")

urlpatterns = [
    path("", include(router.urls)),
    # Zoom integration
    path("zoom/connection/", ZoomConnectionView.as_view(), name="zoom_connection"),
    path("zoom/meetings/", ZoomMeetingsListView.as_view(), name="zoom_meetings"),
]
