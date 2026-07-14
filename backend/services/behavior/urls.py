from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = "behavior_v1"
router = DefaultRouter()
router.register("incidents", views.IncidentViewSet, basename="incident")
router.register("referrals", views.ReferralViewSet, basename="referral")

urlpatterns = [path("", include(router.urls))]
