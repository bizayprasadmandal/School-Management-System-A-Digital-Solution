"""Alumni — School-scoped viewsets."""

from core.pagination import StandardResultsSetPagination
from core.permissions import IsSchoolAdmin, IsSchoolMember
from django.db import models
from django.db.models import Count, IntegerField, OuterRef, Subquery, Value
from django.db.models.functions import Coalesce
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import (
    AlumniChapter,
    AlumniChapterMember,
    AlumniDiscussion,
    AlumniDiscussionLike,
    AlumniDiscussionReply,
    AlumniDonation,
    AlumniDonationReceipt,
    AlumniEvent,
    AlumniEventRSVP,
    AlumniJobApplication,
    AlumniJobPosting,
    AlumniMentorship,
    AlumniProfile,
)
from .serializers import (
    AlumniChapterMemberSerializer,
    AlumniChapterSerializer,
    AlumniDiscussionLikeSerializer,
    AlumniDiscussionReplySerializer,
    AlumniDiscussionSerializer,
    AlumniDonationReceiptSerializer,
    AlumniDonationSerializer,
    AlumniEventRSVPSerializer,
    AlumniEventSerializer,
    AlumniJobApplicationSerializer,
    AlumniJobPostingSerializer,
    AlumniMentorshipSerializer,
    AlumniProfileSerializer,
)


class AlumniProfileViewSet(viewsets.ModelViewSet):
    serializer_class = AlumniProfileSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        "user__first_name",
        "user__last_name",
        "user__email",
        "occupation",
        "employer",
        "city",
    ]
    filterset_fields = ["graduation_year", "employment_status", "city", "country"]
    ordering_fields = ["graduation_year", "user__full_name", "engagement_score"]
    ordering = ["-graduation_year"]

    def get_queryset(self):
        return AlumniProfile.objects.filter(school=self.request.user.school).select_related("user")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated, IsSchoolMember])
    def search(self, request):
        """Search alumni by name, occupation, employer, city."""
        query = request.query_params.get("q", "")
        if not query:
            return Response([], status=status.HTTP_200_OK)
        qs = self.get_queryset().filter(
            models.Q(user__first_name__icontains=query)
            | models.Q(user__last_name__icontains=query)
            | models.Q(occupation__icontains=query)
            | models.Q(employer__icontains=query)
            | models.Q(city__icontains=query)
        )
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class AlumniEventViewSet(viewsets.ModelViewSet):
    serializer_class = AlumniEventSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["title", "description", "location"]
    filterset_fields = ["status"]

    def get_queryset(self):
        return AlumniEvent.objects.filter(school=self.request.user.school).select_related("organizer")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, organizer=self.request.user)


class AlumniEventRSVPViewSet(viewsets.ModelViewSet):
    serializer_class = AlumniEventRSVPSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["event", "status"]

    def get_queryset(self):
        return AlumniEventRSVP.objects.filter(event__school=self.request.user.school).select_related(
            "alumni__user", "event"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated, IsSchoolAdmin])
    def check_in(self, request, pk=None):
        """Mark an RSVP as attended (check-in)."""
        rsvp = self.get_object()
        rsvp.status = AlumniEventRSVP.RSVPStatus.ATTENDED
        rsvp.checked_in_at = timezone.now()
        rsvp.save()
        return Response({"status": "checked_in"})


class AlumniDonationViewSet(viewsets.ModelViewSet):
    serializer_class = AlumniDonationSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["alumni__user__first_name", "alumni__user__last_name", "transaction_id"]
    filterset_fields = ["fund_type", "is_recurring"]

    def get_queryset(self):
        return AlumniDonation.objects.filter(school=self.request.user.school).select_related("alumni__user")

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolAdmin()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class AlumniDonationReceiptViewSet(viewsets.ModelViewSet):
    serializer_class = AlumniDonationReceiptSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status"]

    def get_queryset(self):
        return AlumniDonationReceipt.objects.filter(donation__school=self.request.user.school).select_related(
            "donation__alumni__user"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolAdmin()]

    def perform_create(self, serializer):
        serializer.save()


class AlumniChapterViewSet(viewsets.ModelViewSet):
    serializer_class = AlumniChapterSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name", "city", "country"]
    filterset_fields = ["is_active", "country"]

    def get_queryset(self):
        city_member_count = Subquery(
            AlumniProfile.objects.filter(city__iexact=OuterRef("city"))
            .values("city")
            .annotate(count=Count("id"))
            .values("count"),
            output_field=IntegerField(),
        )
        return AlumniChapter.objects.filter(school=self.request.user.school).annotate(
            member_count=Coalesce(city_member_count, Value(0))
        )

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class AlumniChapterMemberViewSet(viewsets.ModelViewSet):
    serializer_class = AlumniChapterMemberSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["chapter", "role", "is_active"]

    def get_queryset(self):
        return AlumniChapterMember.objects.filter(chapter__school=self.request.user.school).select_related(
            "alumni__user", "chapter"
        )

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()


class AlumniMentorshipViewSet(viewsets.ModelViewSet):
    serializer_class = AlumniMentorshipSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["mentor__user__first_name", "mentor__user__last_name", "mentee__first_name", "mentee__last_name"]
    filterset_fields = ["status", "focus_area"]

    def get_queryset(self):
        return AlumniMentorship.objects.filter(school=self.request.user.school).select_related("mentor__user", "mentee")

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolAdmin()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class AlumniJobPostingViewSet(viewsets.ModelViewSet):
    serializer_class = AlumniJobPostingSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "company", "location"]
    filterset_fields = ["status", "job_type", "experience_level", "is_remote"]
    ordering_fields = ["created_at", "expires_at"]

    def get_queryset(self):
        return AlumniJobPosting.objects.filter(school=self.request.user.school).select_related("posted_by__user")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolMember()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        # Get or create alumni profile for the current user
        try:
            alumni_profile = AlumniProfile.objects.get(user=self.request.user, school=self.request.user.school)
        except AlumniProfile.DoesNotExist:
            return Response({"error": "Alumni profile required to post jobs"}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save(school=self.request.user.school, posted_by=alumni_profile)


class AlumniJobApplicationViewSet(viewsets.ModelViewSet):
    serializer_class = AlumniJobApplicationSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["job", "status"]

    def get_queryset(self):
        return AlumniJobApplication.objects.filter(job__school=self.request.user.school).select_related(
            "applicant", "job"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(applicant=self.request.user)


class AlumniDiscussionViewSet(viewsets.ModelViewSet):
    serializer_class = AlumniDiscussionSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "content"]
    filterset_fields = ["category", "status"]
    ordering_fields = ["created_at", "views_count", "likes_count"]

    def get_queryset(self):
        return AlumniDiscussion.objects.filter(school=self.request.user.school).select_related("author__user")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolMember()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        # Get alumni profile
        try:
            alumni_profile = AlumniProfile.objects.get(user=self.request.user, school=self.request.user.school)
        except AlumniProfile.DoesNotExist:
            return Response({"error": "Alumni profile required"}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save(school=self.request.user.school, author=alumni_profile)

    def retrieve(self, request, *args, **kwargs):
        """Increment views count on retrieve."""
        instance = self.get_object()
        instance.views_count += 1
        instance.save(update_fields=["views_count"])
        return super().retrieve(request, *args, **kwargs)


class AlumniDiscussionReplyViewSet(viewsets.ModelViewSet):
    serializer_class = AlumniDiscussionReplySerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["discussion", "parent"]

    def get_queryset(self):
        return AlumniDiscussionReply.objects.filter(discussion__school=self.request.user.school).select_related(
            "author__user", "discussion"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        # Get alumni profile
        try:
            alumni_profile = AlumniProfile.objects.get(user=self.request.user, school=self.request.user.school)
        except AlumniProfile.DoesNotExist:
            return Response({"error": "Alumni profile required"}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save(author=alumni_profile)


class AlumniDiscussionLikeViewSet(viewsets.ModelViewSet):
    serializer_class = AlumniDiscussionLikeSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["target_type", "discussion", "reply"]

    def get_queryset(self):
        return AlumniDiscussionLike.objects.filter(alumni__school=self.request.user.school).select_related(
            "alumni__user"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        # Get alumni profile
        try:
            alumni_profile = AlumniProfile.objects.get(user=self.request.user, school=self.request.user.school)
        except AlumniProfile.DoesNotExist:
            return Response({"error": "Alumni profile required"}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save(alumni=alumni_profile)
