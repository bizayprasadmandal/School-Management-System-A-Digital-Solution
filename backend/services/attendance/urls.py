from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = "attendance_v1"
router = DefaultRouter()
router.register("", views.AttendanceViewSet, basename="attendance")
router.register("leaves", views.AttendanceLeaveViewSet, basename="leave")

urlpatterns = [path("", include(router.urls))]
