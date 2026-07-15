from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SportViewSet, TeamViewSet, TeamMemberViewSet, SportEventViewSet, SportAchievementViewSet

app_name = "sports_v1"
router = DefaultRouter()
router.register(r"sports", SportViewSet, basename="sport")
router.register(r"teams", TeamViewSet, basename="team")
router.register(r"team-members", TeamMemberViewSet, basename="team-member")
router.register(r"events", SportEventViewSet, basename="sport-event")
router.register(r"achievements", SportAchievementViewSet, basename="sport-achievement")
urlpatterns = [path("", include(router.urls))]
