"""Cafeteria — School-scoped viewsets."""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .models import MealMenu, MealPlan, MealBooking, DietaryRestriction
from .serializers import MealMenuSerializer, MealPlanSerializer, MealBookingSerializer, DietaryRestrictionSerializer
from core.permissions import IsSchoolAdmin, IsSchoolMember
from core.pagination import StandardResultsSetPagination


class MealMenuViewSet(viewsets.ModelViewSet):
    serializer_class = MealMenuSerializer; pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name", "items", "description"]; filterset_fields = ["meal_type", "date", "is_active"]
    def get_queryset(self): return MealMenu.objects.filter(school=self.request.user.school)
    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]
    def perform_create(self, serializer): serializer.save(school=self.request.user.school)


class MealPlanViewSet(viewsets.ModelViewSet):
    serializer_class = MealPlanSerializer; pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name", "description"]; filterset_fields = ["is_active"]
    def get_queryset(self): return MealPlan.objects.filter(school=self.request.user.school)
    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]
    def perform_create(self, serializer): serializer.save(school=self.request.user.school)


class MealBookingViewSet(viewsets.ModelViewSet):
    serializer_class = MealBookingSerializer; pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["user__full_name", "menu__name"]; filterset_fields = ["meal_type", "status", "menu", "booking_date"]
    def get_queryset(self):
        return MealBooking.objects.filter(school=self.request.user.school).select_related("user", "menu", "meal_plan")
    def get_permissions(self): return [IsAuthenticated(), IsSchoolMember()]
    def perform_create(self, serializer): serializer.save(school=self.request.user.school)


class DietaryRestrictionViewSet(viewsets.ModelViewSet):
    serializer_class = DietaryRestrictionSerializer; pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]; filterset_fields = ["user", "restriction_type"]
    def get_queryset(self):
        return DietaryRestriction.objects.filter(user__school=self.request.user.school).select_related("user")
    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]
    def perform_create(self, serializer): serializer.save()
