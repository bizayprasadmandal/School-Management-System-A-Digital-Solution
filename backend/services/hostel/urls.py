"""Hostel / Accommodation Management URL Configuration."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    HostelViewSet, HostelRoomViewSet, HostelAllocationViewSet,
    HostelFeeViewSet, HostelVisitorViewSet,
)

app_name = "hostel_v1"

router = DefaultRouter()
router.register(r"hostels", HostelViewSet, basename="hostel")
router.register(r"rooms", HostelRoomViewSet, basename="room")
router.register(r"allocations", HostelAllocationViewSet, basename="allocation")
router.register(r"fees", HostelFeeViewSet, basename="fee")
router.register(r"visitors", HostelVisitorViewSet, basename="visitor")

urlpatterns = [
    path("", include(router.urls)),
]
