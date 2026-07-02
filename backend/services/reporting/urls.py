from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = "reporting_v1"
router = DefaultRouter()
router.register("", views.ReportingViewSet, basename="reporting")

urlpatterns = [path("", include(router.urls))]
