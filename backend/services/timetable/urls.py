from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = "timetable_v1"
router = DefaultRouter()
router.register("slots", views.TimetableSlotViewSet, basename="slot")
router.register("periods", views.PeriodViewSet, basename="period")
router.register("events", views.SchoolEventViewSet, basename="event")

urlpatterns = [path("", include(router.urls))]
