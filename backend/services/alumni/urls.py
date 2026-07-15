from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AlumniProfileViewSet, AlumniEventViewSet, AlumniDonationViewSet, AlumniChapterViewSet
app_name = "alumni_v1"
router = DefaultRouter()
router.register(r"profiles", AlumniProfileViewSet, basename="alumni-profile")
router.register(r"events", AlumniEventViewSet, basename="alumni-event")
router.register(r"donations", AlumniDonationViewSet, basename="alumni-donation")
router.register(r"chapters", AlumniChapterViewSet, basename="alumni-chapter")
urlpatterns = [path("", include(router.urls))]
