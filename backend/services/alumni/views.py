"""Alumni — School-scoped viewsets."""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .models import AlumniProfile, AlumniEvent, AlumniDonation, AlumniChapter
from .serializers import AlumniProfileSerializer, AlumniEventSerializer, AlumniDonationSerializer, AlumniChapterSerializer
from core.permissions import IsSchoolAdmin, IsSchoolMember
from core.pagination import StandardResultsSetPagination


class AlumniProfileViewSet(viewsets.ModelViewSet):
    serializer_class = AlumniProfileSerializer; pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["user__full_name", "user__email", "occupation", "employer", "city"]
    filterset_fields = ["graduation_year", "employment_status", "city", "country"]
    ordering_fields = ["graduation_year", "user__full_name"]
    ordering = ["-graduation_year"]
    def get_queryset(self):
        return AlumniProfile.objects.filter(school=self.request.user.school).select_related("user")
    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]
    def perform_create(self, serializer): serializer.save(school=self.request.user.school)


class AlumniEventViewSet(viewsets.ModelViewSet):
    serializer_class = AlumniEventSerializer; pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["title", "description", "location"]; filterset_fields = ["status"]
    def get_queryset(self):
        return AlumniEvent.objects.filter(school=self.request.user.school).select_related("organizer")
    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]
    def perform_create(self, serializer): serializer.save(school=self.request.user.school, organizer=self.request.user)


class AlumniDonationViewSet(viewsets.ModelViewSet):
    serializer_class = AlumniDonationSerializer; pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["alumni__user__full_name", "transaction_id"]; filterset_fields = ["fund_type", "is_recurring"]
    def get_queryset(self):
        return AlumniDonation.objects.filter(school=self.request.user.school).select_related("alumni__user")
    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolAdmin()]
    def perform_create(self, serializer): serializer.save(school=self.request.user.school)


class AlumniChapterViewSet(viewsets.ModelViewSet):
    serializer_class = AlumniChapterSerializer; pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name", "city", "country"]; filterset_fields = ["is_active", "country"]
    def get_queryset(self):
        return AlumniChapter.objects.filter(school=self.request.user.school)
    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]
    def perform_create(self, serializer): serializer.save(school=self.request.user.school)
