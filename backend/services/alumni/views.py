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
    AlumniActivityFeed,
    AlumniAward,
    AlumniAwardCategory,
    AlumniAwardNomination,
    AlumniBadge,
    AlumniBadgeAward,
    AlumniCalendarEvent,
    AlumniCalendarRSVP,
    AlumniCampaign,
    AlumniCampaignDonation,
    AlumniChapter,
    AlumniChapterMember,
    AlumniConversation,
    AlumniDirectMessage,
    AlumniDirectoryFilter,
    AlumniDiscussion,
    AlumniDiscussionLike,
    AlumniDiscussionReply,
    AlumniDonation,
    AlumniDonationReceipt,
    AlumniDonationRecurring,
    AlumniEmailCampaignAnalytics,
    AlumniEvent,
    AlumniEventRSVP,
    AlumniGroup,
    AlumniGroupMember,
    AlumniGroupPost,
    AlumniJobApplication,
    AlumniJobPosting,
    AlumniMentorship,
    AlumniNewsletter,
    AlumniPhoto,
    AlumniPhotoAlbum,
    AlumniPhotoComment,
    AlumniPodcastEpisode,
    AlumniPodcastSubscription,
    AlumniPoll,
    AlumniPollOption,
    AlumniPollResponse,
    AlumniProfile,
    AlumniProfileCompleteness,
    AlumniProfileView,
    AlumniReferral,
    AlumniSuccessStory,
    AlumniVerification,
    AlumniVideoGallery,
    AlumniVolunteer,
    AlumniVolunteerSignup,
)
from .serializers import (
    AlumniActivityFeedSerializer,
    AlumniAwardCategorySerializer,
    AlumniAwardNominationSerializer,
    AlumniAwardSerializer,
    AlumniBadgeAwardSerializer,
    AlumniBadgeSerializer,
    AlumniCalendarEventSerializer,
    AlumniCalendarRSVPSerializer,
    AlumniCampaignDonationSerializer,
    AlumniCampaignSerializer,
    AlumniChapterMemberSerializer,
    AlumniChapterSerializer,
    AlumniConversationSerializer,
    AlumniDirectMessageSerializer,
    AlumniDirectoryFilterSerializer,
    AlumniDiscussionLikeSerializer,
    AlumniDiscussionReplySerializer,
    AlumniDiscussionSerializer,
    AlumniDonationReceiptSerializer,
    AlumniDonationRecurringSerializer,
    AlumniDonationSerializer,
    AlumniEmailCampaignAnalyticsSerializer,
    AlumniEventRSVPSerializer,
    AlumniEventSerializer,
    AlumniGroupMemberSerializer,
    AlumniGroupPostSerializer,
    AlumniGroupSerializer,
    AlumniJobApplicationSerializer,
    AlumniJobPostingSerializer,
    AlumniMentorshipSerializer,
    AlumniNewsletterSerializer,
    AlumniPhotoAlbumSerializer,
    AlumniPhotoCommentSerializer,
    AlumniPhotoSerializer,
    AlumniPodcastEpisodeSerializer,
    AlumniPodcastSubscriptionSerializer,
    AlumniPollOptionSerializer,
    AlumniPollResponseSerializer,
    AlumniPollSerializer,
    AlumniProfileCompletenessSerializer,
    AlumniProfileSerializer,
    AlumniProfileViewSerializer,
    AlumniReferralSerializer,
    AlumniSuccessStorySerializer,
    AlumniVerificationSerializer,
    AlumniVideoGallerySerializer,
    AlumniVolunteerSerializer,
    AlumniVolunteerSignupSerializer,
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


class AlumniVerificationViewSet(viewsets.ModelViewSet):
    serializer_class = AlumniVerificationSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status", "verification_method"]

    def get_queryset(self):
        return AlumniVerification.objects.filter(alumni__school=self.request.user.school).select_related(
            "alumni__user", "verified_by"
        )

    def get_permissions(self):
        if self.action in ["create"]:
            return [IsAuthenticated(), IsSchoolMember()]
        return [IsAuthenticated(), IsSchoolAdmin()]

    def perform_create(self, serializer):
        # Get alumni profile
        try:
            alumni_profile = AlumniProfile.objects.get(user=self.request.user, school=self.request.user.school)
        except AlumniProfile.DoesNotExist:
            return Response({"error": "Alumni profile required"}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save(alumni=alumni_profile)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated, IsSchoolAdmin])
    def approve(self, request, pk=None):
        """Approve a verification request."""
        verification = self.get_object()
        verification.status = AlumniVerification.Status.VERIFIED
        verification.verified_by = request.user
        verification.verified_at = timezone.now()
        verification.save()
        # Update alumni verification status
        verification.alumni.is_verified = True
        verification.alumni.save(update_fields=["is_verified"])
        return Response({"status": "approved"})

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated, IsSchoolAdmin])
    def reject(self, request, pk=None):
        """Reject a verification request."""
        verification = self.get_object()
        reason = request.data.get("reason", "")
        verification.status = AlumniVerification.Status.REJECTED
        verification.rejection_reason = reason
        verification.verified_by = request.user
        verification.verified_at = timezone.now()
        verification.save()
        return Response({"status": "rejected"})


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
        try:
            alumni_profile = AlumniProfile.objects.get(user=self.request.user, school=self.request.user.school)
        except AlumniProfile.DoesNotExist:
            return Response({"error": "Alumni profile required"}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save(alumni=alumni_profile)


class AlumniNewsletterViewSet(viewsets.ModelViewSet):
    serializer_class = AlumniNewsletterSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status"]

    def get_queryset(self):
        return AlumniNewsletter.objects.filter(school=self.request.user.school).select_related("created_by")

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolAdmin()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, created_by=self.request.user)


class AlumniCampaignViewSet(viewsets.ModelViewSet):
    serializer_class = AlumniCampaignSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "description"]
    filterset_fields = ["status", "campaign_type"]
    ordering_fields = ["created_at", "goal_amount", "raised_amount"]

    def get_queryset(self):
        return AlumniCampaign.objects.filter(school=self.request.user.school).select_related("created_by")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, created_by=self.request.user)


class AlumniCampaignDonationViewSet(viewsets.ModelViewSet):
    serializer_class = AlumniCampaignDonationSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["campaign", "is_matching"]

    def get_queryset(self):
        return AlumniCampaignDonation.objects.filter(campaign__school=self.request.user.school).select_related(
            "campaign", "donation__alumni__user"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolAdmin()]

    def perform_create(self, serializer):
        serializer.save()


class AlumniBadgeViewSet(viewsets.ModelViewSet):
    serializer_class = AlumniBadgeSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["badge_type", "is_active"]

    def get_queryset(self):
        return AlumniBadge.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolAdmin()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class AlumniBadgeAwardViewSet(viewsets.ModelViewSet):
    serializer_class = AlumniBadgeAwardSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["badge", "alumni"]

    def get_queryset(self):
        return AlumniBadgeAward.objects.filter(badge__school=self.request.user.school).select_related(
            "badge", "alumni__user", "awarded_by"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolAdmin()]

    def perform_create(self, serializer):
        award = serializer.save(awarded_by=self.request.user)
        # Update badge total_awarded count
        award.badge.total_awarded += 1
        award.badge.save(update_fields=["total_awarded"])


class AlumniActivityFeedViewSet(viewsets.ModelViewSet):
    serializer_class = AlumniActivityFeedSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["alumni", "activity_type"]
    ordering_fields = ["created_at"]

    def get_queryset(self):
        return AlumniActivityFeed.objects.filter(alumni__school=self.request.user.school).select_related("alumni__user")

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()


class AlumniGroupViewSet(viewsets.ModelViewSet):
    serializer_class = AlumniGroupSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name", "description"]
    filterset_fields = ["group_type", "is_active", "is_private"]

    def get_queryset(self):
        return AlumniGroup.objects.filter(school=self.request.user.school).select_related("admin__user")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        try:
            alumni_profile = AlumniProfile.objects.get(user=self.request.user, school=self.request.user.school)
        except AlumniProfile.DoesNotExist:
            return Response({"error": "Alumni profile required"}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save(school=self.request.user.school, admin=alumni_profile)


class AlumniGroupMemberViewSet(viewsets.ModelViewSet):
    serializer_class = AlumniGroupMemberSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["group", "role", "status"]

    def get_queryset(self):
        return AlumniGroupMember.objects.filter(group__school=self.request.user.school).select_related(
            "alumni__user", "group"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated, IsSchoolAdmin])
    def approve(self, request, pk=None):
        """Approve a group membership request."""
        membership = self.get_object()
        membership.status = AlumniGroupMember.Status.APPROVED
        membership.save()
        # Update group member count
        membership.group.member_count = membership.group.memberships.filter(status="approved").count()
        membership.group.save(update_fields=["member_count"])
        return Response({"status": "approved"})


class AlumniGroupPostViewSet(viewsets.ModelViewSet):
    serializer_class = AlumniGroupPostSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["group", "is_pinned"]

    def get_queryset(self):
        return AlumniGroupPost.objects.filter(group__school=self.request.user.school).select_related(
            "author__user", "group"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        try:
            alumni_profile = AlumniProfile.objects.get(user=self.request.user, school=self.request.user.school)
        except AlumniProfile.DoesNotExist:
            return Response({"error": "Alumni profile required"}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save(author=alumni_profile)


class AlumniVolunteerViewSet(viewsets.ModelViewSet):
    serializer_class = AlumniVolunteerSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["title", "description"]
    filterset_fields = ["status", "time_commitment", "is_remote"]

    def get_queryset(self):
        return AlumniVolunteer.objects.filter(school=self.request.user.school).select_related("organizer")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, organizer=self.request.user)


class AlumniVolunteerSignupViewSet(viewsets.ModelViewSet):
    serializer_class = AlumniVolunteerSignupSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["opportunity", "status"]

    def get_queryset(self):
        return AlumniVolunteerSignup.objects.filter(opportunity__school=self.request.user.school).select_related(
            "alumni__user", "opportunity"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        try:
            alumni_profile = AlumniProfile.objects.get(user=self.request.user, school=self.request.user.school)
        except AlumniProfile.DoesNotExist:
            return Response({"error": "Alumni profile required"}, status=status.HTTP_400_BAD_REQUEST)
        signup = serializer.save(alumni=alumni_profile)
        # Update volunteer current count
        signup.opportunity.current_volunteers += 1
        signup.opportunity.save(update_fields=["current_volunteers"])


class AlumniPollViewSet(viewsets.ModelViewSet):
    serializer_class = AlumniPollSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["poll_type", "status"]

    def get_queryset(self):
        return AlumniPoll.objects.filter(school=self.request.user.school).select_related("created_by")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, created_by=self.request.user)


class AlumniPollOptionViewSet(viewsets.ModelViewSet):
    serializer_class = AlumniPollOptionSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["poll"]

    def get_queryset(self):
        return AlumniPollOption.objects.filter(poll__school=self.request.user.school)

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()


class AlumniPollResponseViewSet(viewsets.ModelViewSet):
    serializer_class = AlumniPollResponseSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["poll", "alumni"]

    def get_queryset(self):
        return AlumniPollResponse.objects.filter(poll__school=self.request.user.school).select_related(
            "alumni__user", "option"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        try:
            alumni_profile = AlumniProfile.objects.get(user=self.request.user, school=self.request.user.school)
        except AlumniProfile.DoesNotExist:
            return Response({"error": "Alumni profile required"}, status=status.HTTP_400_BAD_REQUEST)
        response = serializer.save(alumni=alumni_profile)
        # Update vote count
        response.option.vote_count += 1
        response.option.save(update_fields=["vote_count"])
        # Update poll total responses
        response.poll.total_responses += 1
        response.poll.save(update_fields=["total_responses"])


class AlumniSuccessStoryViewSet(viewsets.ModelViewSet):
    serializer_class = AlumniSuccessStorySerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "content"]
    filterset_fields = ["story_type", "status", "featured"]
    ordering_fields = ["published_at", "views_count", "likes_count"]

    def get_queryset(self):
        return AlumniSuccessStory.objects.filter(school=self.request.user.school).select_related("alumni__user")

    def get_permissions(self):
        if self.action in ["create"]:
            return [IsAuthenticated(), IsSchoolMember()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        try:
            alumni_profile = AlumniProfile.objects.get(user=self.request.user, school=self.request.user.school)
        except AlumniProfile.DoesNotExist:
            return Response({"error": "Alumni profile required"}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save(school=self.request.user.school, alumni=alumni_profile)

    def retrieve(self, request, *args, **kwargs):
        """Increment views count on retrieve."""
        instance = self.get_object()
        instance.views_count += 1
        instance.save(update_fields=["views_count"])
        return super().retrieve(request, *args, **kwargs)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated, IsSchoolAdmin])
    def approve(self, request, pk=None):
        """Approve and publish a success story."""
        story = self.get_object()
        story.status = AlumniSuccessStory.Status.PUBLISHED
        story.published_at = timezone.now()
        story.save()
        return Response({"status": "published"})


class AlumniReferralViewSet(viewsets.ModelViewSet):
    serializer_class = AlumniReferralSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["referral_type", "status"]

    def get_queryset(self):
        return AlumniReferral.objects.filter(school=self.request.user.school).select_related(
            "referrer__user", "job_posting"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        try:
            alumni_profile = AlumniProfile.objects.get(user=self.request.user, school=self.request.user.school)
        except AlumniProfile.DoesNotExist:
            return Response({"error": "Alumni profile required"}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save(school=self.request.user.school, referrer=alumni_profile)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated, IsSchoolAdmin])
    def convert(self, request, pk=None):
        """Mark a referral as converted."""
        referral = self.get_object()
        referral.status = AlumniReferral.Status.CONVERTED
        referral.converted_at = timezone.now()
        referral.save()
        # Award reward points to referrer
        referral.referrer.engagement_score = min(100, referral.referrer.engagement_score + 10)
        referral.referrer.save(update_fields=["engagement_score"])
        return Response({"status": "converted"})


class AlumniDirectMessageViewSet(viewsets.ModelViewSet):
    serializer_class = AlumniDirectMessageSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["sender", "receiver", "is_read"]

    def get_queryset(self):
        return AlumniDirectMessage.objects.filter(
            models.Q(sender__school=self.request.user.school) | models.Q(receiver__school=self.request.user.school)
        ).select_related("sender__user", "receiver__user")

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        try:
            alumni_profile = AlumniProfile.objects.get(user=self.request.user, school=self.request.user.school)
        except AlumniProfile.DoesNotExist:
            return Response({"error": "Alumni profile required"}, status=status.HTTP_400_BAD_REQUEST)
        message = serializer.save(sender=alumni_profile)
        # Update conversation
        conversation, _ = AlumniConversation.objects.get_or_create(
            participant1=min(message.sender, message.receiver, key=lambda x: x.id),
            participant2=max(message.sender, message.receiver, key=lambda x: x.id),
        )
        conversation.last_message = message
        conversation.last_message_at = message.created_at
        conversation.save(update_fields=["last_message", "last_message_at"])

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated, IsSchoolMember])
    def mark_read(self, request, pk=None):
        """Mark a message as read."""
        message = self.get_object()
        message.is_read = True
        message.read_at = timezone.now()
        message.save(update_fields=["is_read", "read_at"])
        return Response({"status": "marked_read"})


class AlumniConversationViewSet(viewsets.ModelViewSet):
    serializer_class = AlumniConversationSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        return AlumniConversation.objects.filter(
            models.Q(participant1__school=self.request.user.school)
            | models.Q(participant2__school=self.request.user.school)
        ).select_related("participant1__user", "participant2__user", "last_message")

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated, IsSchoolMember])
    def archive(self, request, pk=None):
        """Archive a conversation for the current user."""
        conversation = self.get_object()
        try:
            alumni_profile = AlumniProfile.objects.get(user=self.request.user, school=self.request.user.school)
        except AlumniProfile.DoesNotExist:
            return Response({"error": "Alumni profile required"}, status=status.HTTP_400_BAD_REQUEST)
        if conversation.participant1 == alumni_profile:
            conversation.is_archived_by_p1 = True
        elif conversation.participant2 == alumni_profile:
            conversation.is_archived_by_p2 = True
        conversation.save()
        return Response({"status": "archived"})


class AlumniCalendarEventViewSet(viewsets.ModelViewSet):
    serializer_class = AlumniCalendarEventSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["title", "description", "location"]
    filterset_fields = ["event_type", "is_virtual", "is_published"]

    def get_queryset(self):
        return AlumniCalendarEvent.objects.filter(school=self.request.user.school).select_related("organizer")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        import uuid as uuid_mod

        serializer.save(school=self.request.user.school, organizer=self.request.user, ical_uid=str(uuid_mod.uuid4()))

    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated, IsSchoolMember])
    def ical(self, request, pk=None):
        """Export event as iCal format."""
        event = self.get_object()
        from django.http import HttpResponse

        response = HttpResponse(event.generate_ical(), content_type="text/calendar")
        response["Content-Disposition"] = f'attachment; filename="{event.title}.ics"'
        return response


class AlumniCalendarRSVPViewSet(viewsets.ModelViewSet):
    serializer_class = AlumniCalendarRSVPSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["event", "status"]

    def get_queryset(self):
        return AlumniCalendarRSVP.objects.filter(event__school=self.request.user.school).select_related(
            "alumni__user", "event"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()


class AlumniPhotoAlbumViewSet(viewsets.ModelViewSet):
    serializer_class = AlumniPhotoAlbumSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["title", "description"]
    filterset_fields = ["is_public", "event"]

    def get_queryset(self):
        return AlumniPhotoAlbum.objects.filter(school=self.request.user.school).select_related(
            "created_by__user", "event"
        )

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolMember()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        try:
            alumni_profile = AlumniProfile.objects.get(user=self.request.user, school=self.request.user.school)
        except AlumniProfile.DoesNotExist:
            return Response({"error": "Alumni profile required"}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save(school=self.request.user.school, created_by=alumni_profile)


class AlumniPhotoViewSet(viewsets.ModelViewSet):
    serializer_class = AlumniPhotoSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["album", "is_featured"]

    def get_queryset(self):
        return AlumniPhoto.objects.filter(album__school=self.request.user.school).select_related(
            "album", "uploaded_by__user"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        try:
            alumni_profile = AlumniProfile.objects.get(user=self.request.user, school=self.request.user.school)
        except AlumniProfile.DoesNotExist:
            return Response({"error": "Alumni profile required"}, status=status.HTTP_400_BAD_REQUEST)
        photo = serializer.save(uploaded_by=alumni_profile)
        # Update album photo count
        photo.album.photo_count += 1
        photo.album.save(update_fields=["photo_count"])


class AlumniPhotoCommentViewSet(viewsets.ModelViewSet):
    serializer_class = AlumniPhotoCommentSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["photo"]

    def get_queryset(self):
        return AlumniPhotoComment.objects.filter(photo__album__school=self.request.user.school).select_related(
            "author__user", "photo"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        try:
            alumni_profile = AlumniProfile.objects.get(user=self.request.user, school=self.request.user.school)
        except AlumniProfile.DoesNotExist:
            return Response({"error": "Alumni profile required"}, status=status.HTTP_400_BAD_REQUEST)
        comment = serializer.save(author=alumni_profile)
        # Update photo comment count
        comment.photo.comments_count += 1
        comment.photo.save(update_fields=["comments_count"])


class AlumniVideoGalleryViewSet(viewsets.ModelViewSet):
    serializer_class = AlumniVideoGallerySerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "description", "tags"]
    filterset_fields = ["video_type", "is_featured"]
    ordering_fields = ["uploaded_at", "view_count", "like_count"]

    def get_queryset(self):
        return AlumniVideoGallery.objects.filter(school=self.request.user.school).select_related(
            "uploaded_by__user", "event"
        )

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolMember()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        try:
            alumni_profile = AlumniProfile.objects.get(user=self.request.user, school=self.request.user.school)
        except AlumniProfile.DoesNotExist:
            return Response({"error": "Alumni profile required"}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save(school=self.request.user.school, uploaded_by=alumni_profile)

    def retrieve(self, request, *args, **kwargs):
        """Increment view count on retrieve."""
        instance = self.get_object()
        instance.view_count += 1
        instance.save(update_fields=["view_count"])
        return super().retrieve(request, *args, **kwargs)


class AlumniDirectoryFilterViewSet(viewsets.ModelViewSet):
    serializer_class = AlumniDirectoryFilterSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["is_public"]

    def get_queryset(self):
        return AlumniDirectoryFilter.objects.filter(alumni__school=self.request.user.school).select_related(
            "alumni__user"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        try:
            alumni_profile = AlumniProfile.objects.get(user=self.request.user, school=self.request.user.school)
        except AlumniProfile.DoesNotExist:
            return Response({"error": "Alumni profile required"}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save(alumni=alumni_profile)


class AlumniProfileViewViewSet(viewsets.ModelViewSet):
    serializer_class = AlumniProfileViewSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["viewer", "viewed"]

    def get_queryset(self):
        return AlumniProfileView.objects.filter(
            models.Q(viewer__school=self.request.user.school) | models.Q(viewed__school=self.request.user.school)
        ).select_related("viewer__user", "viewed__user")

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        try:
            alumni_profile = AlumniProfile.objects.get(user=self.request.user, school=self.request.user.school)
        except AlumniProfile.DoesNotExist:
            return Response({"error": "Alumni profile required"}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save(viewer=alumni_profile)


class AlumniProfileCompletenessViewSet(viewsets.ModelViewSet):
    serializer_class = AlumniProfileCompletenessSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        return AlumniProfileCompleteness.objects.filter(alumni__school=self.request.user.school).select_related(
            "alumni__user"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated, IsSchoolMember])
    def calculate(self, request, pk=None):
        """Recalculate profile completion."""
        completeness = self.get_object()
        percentage = completeness.calculate_completion()
        return Response({"completion_percentage": percentage})


class AlumniEmailCampaignAnalyticsViewSet(viewsets.ModelViewSet):
    serializer_class = AlumniEmailCampaignAnalyticsSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["newsletter", "event_type"]

    def get_queryset(self):
        return AlumniEmailCampaignAnalytics.objects.filter(newsletter__school=self.request.user.school).select_related(
            "newsletter", "alumni__user"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolAdmin()]

    def perform_create(self, serializer):
        serializer.save()


class AlumniDonationRecurringViewSet(viewsets.ModelViewSet):
    serializer_class = AlumniDonationRecurringSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status", "frequency"]

    def get_queryset(self):
        return AlumniDonationRecurring.objects.filter(alumni__school=self.request.user.school).select_related(
            "alumni__user"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        try:
            alumni_profile = AlumniProfile.objects.get(user=self.request.user, school=self.request.user.school)
        except AlumniProfile.DoesNotExist:
            return Response({"error": "Alumni profile required"}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save(alumni=alumni_profile)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated, IsSchoolMember])
    def pause(self, request, pk=None):
        """Pause a recurring donation."""
        recurring = self.get_object()
        recurring.status = AlumniDonationRecurring.Status.PAUSED
        recurring.save(update_fields=["status"])
        return Response({"status": "paused"})

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated, IsSchoolMember])
    def cancel(self, request, pk=None):
        """Cancel a recurring donation."""
        recurring = self.get_object()
        recurring.status = AlumniDonationRecurring.Status.CANCELLED
        recurring.save(update_fields=["status"])
        return Response({"status": "cancelled"})


class AlumniPodcastEpisodeViewSet(viewsets.ModelViewSet):
    serializer_class = AlumniPodcastEpisodeSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "description", "tags"]
    filterset_fields = ["episode_type", "status"]
    ordering_fields = ["published_at", "play_count", "like_count"]

    def get_queryset(self):
        return AlumniPodcastEpisode.objects.filter(school=self.request.user.school).select_related("host__user")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        try:
            alumni_profile = AlumniProfile.objects.get(user=self.request.user, school=self.request.user.school)
        except AlumniProfile.DoesNotExist:
            return Response({"error": "Alumni profile required"}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save(school=self.request.user.school, host=alumni_profile)

    def retrieve(self, request, *args, **kwargs):
        """Increment play count on retrieve."""
        instance = self.get_object()
        instance.play_count += 1
        instance.save(update_fields=["play_count"])
        return super().retrieve(request, *args, **kwargs)


class AlumniPodcastSubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = AlumniPodcastSubscriptionSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["is_active"]

    def get_queryset(self):
        return AlumniPodcastSubscription.objects.filter(alumni__school=self.request.user.school).select_related(
            "alumni__user"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        try:
            alumni_profile = AlumniProfile.objects.get(user=self.request.user, school=self.request.user.school)
        except AlumniProfile.DoesNotExist:
            return Response({"error": "Alumni profile required"}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save(alumni=alumni_profile)


class AlumniAwardCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = AlumniAwardCategorySerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["is_active"]

    def get_queryset(self):
        return AlumniAwardCategory.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolAdmin()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class AlumniAwardViewSet(viewsets.ModelViewSet):
    serializer_class = AlumniAwardSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["title", "description"]
    filterset_fields = ["status", "year", "category"]

    def get_queryset(self):
        return AlumniAward.objects.filter(school=self.request.user.school).select_related("category", "created_by")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, created_by=self.request.user)


class AlumniAwardNominationViewSet(viewsets.ModelViewSet):
    serializer_class = AlumniAwardNominationSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["award", "status"]

    def get_queryset(self):
        return AlumniAwardNomination.objects.filter(award__school=self.request.user.school).select_related(
            "nominee__user", "nominated_by__user", "award"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        try:
            alumni_profile = AlumniProfile.objects.get(user=self.request.user, school=self.request.user.school)
        except AlumniProfile.DoesNotExist:
            return Response({"error": "Alumni profile required"}, status=status.HTTP_400_BAD_REQUEST)
        nomination = serializer.save(nominated_by=alumni_profile)
        # Update award nomination count
        nomination.award.total_nominations += 1
        nomination.award.save(update_fields=["total_nominations"])
