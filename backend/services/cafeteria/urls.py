from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MealMenuViewSet, MealPlanViewSet, MealBookingViewSet, DietaryRestrictionViewSet
app_name = "cafeteria_v1"
router = DefaultRouter()
router.register(r"menus", MealMenuViewSet, basename="meal-menu")
router.register(r"plans", MealPlanViewSet, basename="meal-plan")
router.register(r"bookings", MealBookingViewSet, basename="meal-booking")
router.register(r"dietary", DietaryRestrictionViewSet, basename="dietary")
urlpatterns = [path("", include(router.urls))]
