from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = "communication_v1"
router = DefaultRouter()
router.register("announcements", views.AnnouncementViewSet, basename="announcement")
router.register("messages", views.DirectMessageViewSet, basename="message")
router.register("notifications", views.NotificationViewSet, basename="notification")

urlpatterns = [path("", include(router.urls))]
