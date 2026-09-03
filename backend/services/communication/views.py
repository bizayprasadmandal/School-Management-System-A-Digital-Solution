"""
Communication Service — DRF Views for announcements, messages, notifications
"""

from core.pagination import StandardResultsSetPagination
from core.permissions import IsSchoolAdmin, IsSchoolMember
from django.db.models import Count, Q
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import (
    Announcement,
    AnnouncementRead,
    BroadcastMessage,
    ChatGroup,
    CommunicationAnalytics,
    CommunicationBlacklist,
    CommunicationLog,
    CommunicationPreference,
    ConferenceParticipant,
    DeviceToken,
    DirectMessage,
    EmailIntegration,
    EmailTemplate,
    EmergencyAlert,
    FileAttachment,
    GroupMembership,
    GroupMessage,
    MessageDeliveryStatus,
    MessageReaction,
    MessageTemplate,
    MessageThread,
    Newsletter,
    Notification,
    NotificationSchedule,
    NotificationTemplate,
    ParentTeacherChat,
    ParentTeacherMessage,
    Poll,
    PollVote,
    ReadReceipt,
    SMSGatewayConfig,
    SMSIntegration,
    SMSLog,
    Survey,
    SurveyResponse,
    TypingIndicator,
    VideoConference,
    VoiceMessage,
)
from .serializers import (
    AnnouncementReadSerializer,
    AnnouncementSerializer,
    BroadcastMessageSerializer,
    ChatGroupSerializer,
    CommunicationAnalyticsSerializer,
    CommunicationBlacklistSerializer,
    CommunicationLogSerializer,
    CommunicationPreferenceSerializer,
    ConferenceParticipantSerializer,
    DeviceTokenSerializer,
    DirectMessageSerializer,
    EmailIntegrationSerializer,
    EmailTemplateSerializer,
    EmergencyAlertSerializer,
    FileAttachmentSerializer,
    GroupMembershipSerializer,
    GroupMessageSerializer,
    MessageDeliveryStatusSerializer,
    MessageReactionSerializer,
    MessageTemplateSerializer,
    MessageThreadSerializer,
    NewsletterSerializer,
    NotificationScheduleSerializer,
    NotificationSerializer,
    NotificationTemplateSerializer,
    ParentTeacherChatSerializer,
    ParentTeacherMessageSerializer,
    PollSerializer,
    PollVoteSerializer,
    ReadReceiptSerializer,
    SMSGatewayConfigSerializer,
    SMSIntegrationSerializer,
    SMSLogSerializer,
    SurveyResponseSerializer,
    SurveySerializer,
    TypingIndicatorSerializer,
    VideoConferenceSerializer,
    VoiceMessageSerializer,
)
from .services import broadcast_announcement


class AnnouncementViewSet(viewsets.ModelViewSet):
    """
    Announcements CRUD.
    - Admins/Teachers: create, publish, delete
    - Students/Parents: read-only, filtered by audience
    """

    serializer_class = AnnouncementSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["priority", "audience", "is_draft"]
    search_fields = ["title", "content"]
    ordering_fields = ["created_at", "published_at", "priority"]
    ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user
        qs = Announcement.objects.filter(school=user.school)

        if user.role in ["student", "parent"]:
            audience_map = {"student": ["all", "students"], "parent": ["all", "parents"]}
            qs = qs.filter(
                is_draft=False,
                audience__in=audience_map.get(user.role, ["all"]),
            ).filter(expires_at__isnull=True) | qs.filter(
                is_draft=False,
                audience__in=audience_map.get(user.role, ["all"]),
                expires_at__gt=timezone.now(),
            )
        return qs.distinct()

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy", "publish"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        announcement = serializer.save(
            school=self.request.user.school,
            created_by=self.request.user,
        )
        if not announcement.is_draft:
            announcement.published_at = timezone.now()
            announcement.save(update_fields=["published_at"])
            broadcast_announcement.delay(str(announcement.id))

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        """Publish a draft announcement and broadcast to users."""
        announcement = self.get_object()
        if not announcement.is_draft:
            return Response({"detail": "Already published."}, status=status.HTTP_400_BAD_REQUEST)
        announcement.is_draft = False
        announcement.published_at = timezone.now()
        announcement.save(update_fields=["is_draft", "published_at"])
        broadcast_announcement.delay(str(announcement.id))
        return Response({"detail": "Announcement published and broadcast queued."})

    @action(detail=True, methods=["post"], url_path="mark-read")
    def mark_read(self, request, pk=None):
        announcement = self.get_object()
        from .models import AnnouncementRead

        AnnouncementRead.objects.get_or_create(announcement=announcement, user=request.user)
        announcement.view_count += 1
        announcement.save(update_fields=["view_count"])
        return Response({"detail": "Marked as read."})


class DirectMessageViewSet(viewsets.ModelViewSet):
    """
    Direct messaging between users within the same school.
    """

    serializer_class = DirectMessageSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, IsSchoolMember]
    http_method_names = ["get", "post", "delete"]

    def get_queryset(self):
        user = self.request.user
        return DirectMessage.objects.filter(sender=user) | DirectMessage.objects.filter(recipient=user).exclude(
            is_deleted_recipient=True
        ).select_related("sender", "recipient").order_by("-sent_at")

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

    @action(detail=False, methods=["get"], url_path="conversation/(?P<user_id>[^/.]+)")
    def conversation(self, request, user_id=None):
        """Retrieve conversation thread between the authenticated user and another."""
        from django.contrib.auth import get_user_model
        from rest_framework.exceptions import PermissionDenied

        user = request.user
        User = get_user_model()
        try:
            other = User.objects.get(id=user_id)
        except (User.DoesNotExist, ValueError):
            raise PermissionDenied("Conversation partner not found.")
        # Cross-school messaging is not allowed: the conversation partner must
        # belong to the same school as the caller.
        if other.school != user.school:
            raise PermissionDenied("You can only message users in your school.")

        messages = DirectMessage.objects.filter(
            sender=user,
            recipient_id=user_id,
        ) | DirectMessage.objects.filter(
            sender_id=user_id,
            recipient=user,
        )
        messages = messages.select_related("sender", "recipient").order_by("sent_at")

        # Mark received messages as read
        messages.filter(recipient=user, status="delivered").update(status="read", read_at=timezone.now())

        page = self.paginate_queryset(messages)
        if page is not None:
            return self.get_paginated_response(DirectMessageSerializer(page, many=True).data)
        return Response(DirectMessageSerializer(messages, many=True).data)

    @action(detail=False, methods=["get"], url_path="inbox")
    def inbox(self, request):
        """Latest message per conversation partner."""
        user = request.user
        messages = DirectMessage.objects.filter(Q(sender=user) | Q(recipient=user)).order_by("-sent_at")

        # Single query for unread counts per sender (avoids N+1 per partner)
        unread_counts = (
            DirectMessage.objects.filter(recipient=user, status__in=["sent", "delivered"])
            .values("sender")
            .annotate(count=Count("id"))
        )
        unread_map = {str(item["sender"]): item["count"] for item in unread_counts}

        seen_partners = set()
        threads = []
        for msg in messages:
            partner = msg.recipient if msg.sender == user else msg.sender
            if partner.id not in seen_partners:
                seen_partners.add(partner.id)
                threads.append(
                    {
                        "partner": {
                            "id": str(partner.id),
                            "name": partner.full_name,
                            "role": partner.role,
                            "avatar": partner.avatar.url if partner.avatar else None,
                        },
                        "last_message": DirectMessageSerializer(msg).data,
                        "unread_count": unread_map.get(str(partner.id), 0),
                    }
                )
        return Response(threads)


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only notification list for the authenticated user.
    """

    serializer_class = NotificationSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["channel", "status"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @action(detail=True, methods=["patch"], url_path="mark-read")
    def mark_read(self, request, pk=None):
        notif = self.get_object()
        notif.status = "read"
        notif.read_at = timezone.now()
        notif.save(update_fields=["status", "read_at"])
        return Response({"detail": "Marked as read."})

    @action(detail=False, methods=["post"], url_path="mark-all-read")
    def mark_all_read(self, request):
        count = Notification.objects.filter(user=request.user, read_at__isnull=True).update(
            status="read", read_at=timezone.now()
        )
        return Response({"marked_read": count})

    @action(detail=False, methods=["get"], url_path="unread-count")
    def unread_count(self, request):
        count = Notification.objects.filter(user=request.user, channel="in_app", read_at__isnull=True).count()
        return Response({"count": count})


class DeviceTokenView(viewsets.ViewSet):
    """
    Register or update an Expo push notification token for the
    authenticated user's current device.

    POST /api/v1/communication/push-tokens/ — create or update token
    DELETE /api/v1/communication/push-tokens/<token>/ — deactivate token
    """

    permission_classes = [IsAuthenticated, IsSchoolMember]
    serializer_class = DeviceTokenSerializer

    def create(self, request):
        serializer = DeviceTokenSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        token = serializer.save()
        return Response(
            DeviceTokenSerializer(token).data,
            status=status.HTTP_201_CREATED,
        )

    def destroy(self, request, pk=None):
        """Deactivate a push token by its value (not ID)."""
        # pk here is the token string from the URL
        updated = DeviceToken.objects.filter(user=request.user, token=pk).update(is_active=False)
        if updated:
            return Response({"detail": "Token deactivated."})
        return Response(
            {"detail": "Token not found."},
            status=status.HTTP_404_NOT_FOUND,
        )


# =============================================================================
# Group Messaging Views
# =============================================================================


class ChatGroupViewSet(viewsets.ModelViewSet):
    serializer_class = ChatGroupSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, IsSchoolMember]

    def get_queryset(self):
        user = self.request.user
        return ChatGroup.objects.filter(school=user.school, memberships__user=user)

    def perform_create(self, serializer):
        group = serializer.save(school=self.request.user.school, created_by=self.request.user)
        # Auto-add creator as owner
        GroupMembership.objects.create(group=group, user=self.request.user, role=GroupMembership.Role.OWNER)

    @action(detail=True, methods=["post"], url_path="add-member")
    def add_member(self, request, pk=None):
        group = self.get_object()
        user_id = request.data.get("user_id")
        if not user_id:
            return Response({"error": "user_id is required"}, status=400)
        from django.contrib.auth import get_user_model

        User = get_user_model()
        try:
            member_user = User.objects.get(id=user_id, school=request.user.school)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
        membership, created = GroupMembership.objects.get_or_create(
            group=group, user=member_user, defaults={"role": request.data.get("role", GroupMembership.Role.MEMBER)}
        )
        if not created:
            return Response({"error": "User already in group"}, status=400)
        return Response({"detail": "Member added"}, status=201)

    @action(detail=True, methods=["post"], url_path="remove-member")
    def remove_member(self, request, pk=None):
        group = self.get_object()
        user_id = request.data.get("user_id")
        if not user_id:
            return Response({"error": "user_id is required"}, status=400)
        deleted, _ = GroupMembership.objects.filter(group=group, user_id=user_id).delete()
        if deleted:
            return Response({"detail": "Member removed"})
        return Response({"error": "Member not found"}, status=404)


class GroupMessageViewSet(viewsets.ModelViewSet):
    serializer_class = GroupMessageSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, IsSchoolMember]

    def get_queryset(self):
        user = self.request.user
        group_id = self.request.query_params.get("group_id")
        if group_id:
            return GroupMessage.objects.filter(group_id=group_id, group__memberships__user=user)
        return GroupMessage.objects.filter(group__memberships__user=user)

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

    @action(detail=True, methods=["post"], url_path="mark-read")
    def mark_read(self, request, pk=None):
        message = self.get_object()
        ReadReceipt.objects.get_or_create(message=message, user=request.user)
        return Response({"detail": "Marked as read"})

    @action(detail=True, methods=["get"], url_path="read-by")
    def read_by(self, request, pk=None):
        message = self.get_object()
        receipts = ReadReceipt.objects.filter(message=message).select_related("user")
        data = [{"user": r.user.id, "name": r.user.full_name, "read_at": r.read_at} for r in receipts]
        return Response(data)


class MessageReactionViewSet(viewsets.ModelViewSet):
    serializer_class = MessageReactionSerializer
    permission_classes = [IsAuthenticated, IsSchoolMember]

    def get_queryset(self):
        message_id = self.request.query_params.get("message_id")
        if message_id:
            return MessageReaction.objects.filter(message_id=message_id)
        return MessageReaction.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ReadReceiptViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ReadReceiptSerializer
    permission_classes = [IsAuthenticated, IsSchoolMember]

    def get_queryset(self):
        message_id = self.request.query_params.get("message_id")
        if message_id:
            return ReadReceipt.objects.filter(message_id=message_id)
        return ReadReceipt.objects.filter(user=self.request.user)


class TypingIndicatorViewSet(viewsets.ModelViewSet):
    serializer_class = TypingIndicatorSerializer
    permission_classes = [IsAuthenticated, IsSchoolMember]

    def get_queryset(self):
        chat_type = self.request.query_params.get("chat_type")
        chat_id = self.request.query_params.get("chat_id")
        if chat_type and chat_id:
            return TypingIndicator.objects.filter(chat_type=chat_type, chat_id=chat_id)
        return TypingIndicator.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        from datetime import timedelta

        expires_at = timezone.now() + timedelta(seconds=10)
        serializer.save(user=self.request.user, expires_at=expires_at)


class MessageThreadViewSet(viewsets.ModelViewSet):
    serializer_class = MessageThreadSerializer
    permission_classes = [IsAuthenticated, IsSchoolMember]

    def get_queryset(self):
        message_id = self.request.query_params.get("message_id")
        if message_id:
            return MessageThread.objects.filter(parent_message_id=message_id)
        return MessageThread.objects.all()


class FileAttachmentViewSet(viewsets.ModelViewSet):
    serializer_class = FileAttachmentSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, IsSchoolMember]

    def get_queryset(self):
        user = self.request.user
        return FileAttachment.objects.filter(school=user.school)

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, uploaded_by=self.request.user)

    @action(detail=True, methods=["post"], url_path="download")
    def download(self, request, pk=None):
        attachment = self.get_object()
        attachment.download_count += 1
        attachment.save(update_fields=["download_count"])
        return Response({"url": attachment.file.url if attachment.file else None})


# =============================================================================
# Parent-Teacher Chat Views
# =============================================================================


class ParentTeacherChatViewSet(viewsets.ModelViewSet):
    serializer_class = ParentTeacherChatSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, IsSchoolMember]

    def get_queryset(self):
        user = self.request.user
        if user.role == "parent":
            return ParentTeacherChat.objects.filter(parent=user)
        elif user.role == "teacher":
            return ParentTeacherChat.objects.filter(teacher=user)
        elif user.role in ["school_admin", "super_admin"]:
            return ParentTeacherChat.objects.filter(school=user.school)
        return ParentTeacherChat.objects.none()

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class ParentTeacherMessageViewSet(viewsets.ModelViewSet):
    serializer_class = ParentTeacherMessageSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, IsSchoolMember]

    def get_queryset(self):
        user = self.request.user
        chat_id = self.request.query_params.get("chat_id")
        if chat_id:
            return ParentTeacherMessage.objects.filter(chat_id=chat_id)
        return ParentTeacherMessage.objects.filter(Q(chat__parent=user) | Q(chat__teacher=user)).select_related(
            "sender"
        )

    def perform_create(self, serializer):
        msg = serializer.save(sender=self.request.user)
        # Update last_message_at on chat
        msg.chat.last_message_at = msg.sent_at
        msg.chat.save(update_fields=["last_message_at"])

    @action(detail=True, methods=["post"], url_path="mark-read")
    def mark_read(self, request, pk=None):
        message = self.get_object()
        user = request.user
        if user == message.chat.parent:
            message.is_read_by_parent = True
        elif user == message.chat.teacher:
            message.is_read_by_teacher = True
        message.save(update_fields=["is_read_by_parent", "is_read_by_teacher"])
        return Response({"detail": "Marked as read"})


# =============================================================================
# Video Conferencing Views
# =============================================================================


class VideoConferenceViewSet(viewsets.ModelViewSet):
    serializer_class = VideoConferenceSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, IsSchoolMember]

    def get_queryset(self):
        user = self.request.user
        return VideoConference.objects.filter(school=user.school)

    def perform_create(self, serializer):
        conference = serializer.save(school=self.request.user.school, host=self.request.user)
        # Auto-add host as participant
        ConferenceParticipant.objects.create(
            conference=conference, user=self.request.user, status=ConferenceParticipant.Status.ACCEPTED
        )

    @action(detail=True, methods=["post"], url_path="invite")
    def invite(self, request, pk=None):
        conference = self.get_object()
        user_ids = request.data.get("user_ids", [])
        invited = 0
        for uid in user_ids:
            _, created = ConferenceParticipant.objects.get_or_create(
                conference=conference, user_id=uid, defaults={"status": ConferenceParticipant.Status.INVITED}
            )
            if created:
                invited += 1
        return Response({"invited": invited})

    @action(detail=True, methods=["post"], url_path="start")
    def start(self, request, pk=None):
        conference = self.get_object()
        conference.status = VideoConference.Status.ACTIVE
        conference.save(update_fields=["status"])
        return Response({"detail": "Conference started"})

    @action(detail=True, methods=["post"], url_path="end")
    def end(self, request, pk=None):
        conference = self.get_object()
        conference.status = VideoConference.Status.ENDED
        conference.save(update_fields=["status"])
        return Response({"detail": "Conference ended"})


class ConferenceParticipantViewSet(viewsets.ModelViewSet):
    serializer_class = ConferenceParticipantSerializer
    permission_classes = [IsAuthenticated, IsSchoolMember]

    def get_queryset(self):
        conference_id = self.request.query_params.get("conference_id")
        if conference_id:
            return ConferenceParticipant.objects.filter(conference_id=conference_id)
        return ConferenceParticipant.objects.filter(user=self.request.user)

    @action(detail=True, methods=["post"], url_path="join")
    def join(self, request, pk=None):
        participant = self.get_object()
        participant.status = ConferenceParticipant.Status.ATTENDED
        participant.joined_at = timezone.now()
        participant.save(update_fields=["status", "joined_at"])
        return Response({"detail": "Joined conference"})

    @action(detail=True, methods=["post"], url_path="leave")
    def leave(self, request, pk=None):
        participant = self.get_object()
        participant.left_at = timezone.now()
        if participant.joined_at:
            duration = (participant.left_at - participant.joined_at).seconds // 60
            participant.duration_minutes = duration
        participant.save(update_fields=["left_at", "duration_minutes"])
        return Response({"detail": "Left conference"})


# =============================================================================
# SMS/Email Integration Views
# =============================================================================


class SMSIntegrationViewSet(viewsets.ModelViewSet):
    serializer_class = SMSIntegrationSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, IsSchoolAdmin]

    def get_queryset(self):
        return SMSIntegration.objects.filter(school=self.request.user.school)

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, sent_by=self.request.user)


class EmailIntegrationViewSet(viewsets.ModelViewSet):
    serializer_class = EmailIntegrationSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, IsSchoolAdmin]

    def get_queryset(self):
        return EmailIntegration.objects.filter(school=self.request.user.school)

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, sent_by=self.request.user)


# =============================================================================
# Broadcast Messages Views
# =============================================================================


class BroadcastMessageViewSet(viewsets.ModelViewSet):
    serializer_class = BroadcastMessageSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, IsSchoolAdmin]

    def get_queryset(self):
        return BroadcastMessage.objects.filter(school=self.request.user.school)

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, created_by=self.request.user)

    @action(detail=True, methods=["post"], url_path="send")
    def send_broadcast(self, request, pk=None):
        broadcast = self.get_object()
        broadcast.status = BroadcastMessage.Status.SENDING
        broadcast.save(update_fields=["status"])
        # In production, this would trigger a Celery task
        return Response({"detail": "Broadcast sending queued"})


# =============================================================================
# Communication Logs Views
# =============================================================================


class CommunicationLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CommunicationLogSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, IsSchoolAdmin]

    def get_queryset(self):
        qs = CommunicationLog.objects.filter(school=self.request.user.school)
        comm_type = self.request.query_params.get("communication_type")
        if comm_type:
            qs = qs.filter(communication_type=comm_type)
        return qs


# =============================================================================
# Voice Messages Views
# =============================================================================


class VoiceMessageViewSet(viewsets.ModelViewSet):
    serializer_class = VoiceMessageSerializer
    permission_classes = [IsAuthenticated, IsSchoolMember]

    def get_queryset(self):
        user = self.request.user
        group_id = self.request.query_params.get("group_id")
        if group_id:
            return VoiceMessage.objects.filter(group_id=group_id, group__memberships__user=user)
        return VoiceMessage.objects.filter(
            Q(group__memberships__user=user)
            | Q(parent_teacher_chat__parent=user)
            | Q(parent_teacher_chat__teacher=user)
        )

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)


# ── Additional ViewSets (module expansion) ──


class AnnouncementReadViewSet(viewsets.ModelViewSet):
    serializer_class = AnnouncementReadSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return AnnouncementRead.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class NotificationTemplateViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationTemplateSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return NotificationTemplate.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class DeviceTokenViewSet(viewsets.ModelViewSet):
    serializer_class = DeviceTokenSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return DeviceToken.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class GroupMembershipViewSet(viewsets.ModelViewSet):
    serializer_class = GroupMembershipSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return GroupMembership.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class SurveyViewSet(viewsets.ModelViewSet):
    serializer_class = SurveySerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return Survey.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class SurveyResponseViewSet(viewsets.ModelViewSet):
    serializer_class = SurveyResponseSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return SurveyResponse.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class PollViewSet(viewsets.ModelViewSet):
    serializer_class = PollSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return Poll.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class PollVoteViewSet(viewsets.ModelViewSet):
    serializer_class = PollVoteSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return PollVote.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class EmailTemplateViewSet(viewsets.ModelViewSet):
    serializer_class = EmailTemplateSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return EmailTemplate.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class SMSGatewayConfigViewSet(viewsets.ModelViewSet):
    serializer_class = SMSGatewayConfigSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return SMSGatewayConfig.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class SMSLogViewSet(viewsets.ModelViewSet):
    serializer_class = SMSLogSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return SMSLog.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class NewsletterViewSet(viewsets.ModelViewSet):
    serializer_class = NewsletterSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return Newsletter.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class EmergencyAlertViewSet(viewsets.ModelViewSet):
    serializer_class = EmergencyAlertSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return EmergencyAlert.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class CommunicationPreferenceViewSet(viewsets.ModelViewSet):
    serializer_class = CommunicationPreferenceSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return CommunicationPreference.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class MessageTemplateViewSet(viewsets.ModelViewSet):
    serializer_class = MessageTemplateSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return MessageTemplate.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class MessageDeliveryStatusViewSet(viewsets.ModelViewSet):
    serializer_class = MessageDeliveryStatusSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return MessageDeliveryStatus.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class CommunicationBlacklistViewSet(viewsets.ModelViewSet):
    serializer_class = CommunicationBlacklistSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return CommunicationBlacklist.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class CommunicationAnalyticsViewSet(viewsets.ModelViewSet):
    serializer_class = CommunicationAnalyticsSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return CommunicationAnalytics.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class NotificationScheduleViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationScheduleSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return NotificationSchedule.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)
