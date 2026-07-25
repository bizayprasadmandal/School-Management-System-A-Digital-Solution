"""
Communication Service — DRF Views for announcements, messages, notifications
"""

from django.utils import timezone
from django.db.models import Q, Count, Max, OuterRef, Subquery
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .models import Announcement, DirectMessage, Notification
from .serializers import (
    AnnouncementSerializer, DirectMessageSerializer, NotificationSerializer,
    DeviceTokenSerializer,
)
from .services import broadcast_announcement
from core.permissions import IsSchoolMember, IsTeacher, IsSchoolAdmin
from core.pagination import StandardResultsSetPagination


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
            ).filter(
                expires_at__isnull=True
            ) | qs.filter(
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
        AnnouncementRead.objects.get_or_create(
            announcement=announcement, user=request.user
        )
        announcement.view_count += 1
        announcement.save(update_fields=["view_count"])
        return Response({"detail": "Marked as read."})


class DirectMessageViewSet(viewsets.ModelViewSet):
    """
    Direct messaging between users within the same school.
    """

    serializer_class = DirectMessageSerializer
    pagination_class = StandardResultsSetPagination
    http_method_names = ["get", "post", "delete"]

    def get_queryset(self):
        user = self.request.user
        return DirectMessage.objects.filter(
            sender=user
        ) | DirectMessage.objects.filter(
            recipient=user
        ).exclude(
            is_deleted_recipient=True
        ).select_related(
            "sender", "recipient"
        ).order_by("-sent_at")

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

    @action(detail=False, methods=["get"], url_path="conversation/(?P<user_id>[^/.]+)")
    def conversation(self, request, user_id=None):
        """Retrieve conversation thread between the authenticated user and another."""
        user = request.user
        messages = DirectMessage.objects.filter(
            sender=user, recipient_id=user_id,
        ) | DirectMessage.objects.filter(
            sender_id=user_id, recipient=user,
        )
        messages = messages.select_related(
            "sender", "recipient"
        ).order_by("sent_at")

        # Mark received messages as read
        messages.filter(recipient=user, status="delivered").update(
            status="read", read_at=timezone.now()
        )

        page = self.paginate_queryset(messages)
        if page is not None:
            return self.get_paginated_response(
                DirectMessageSerializer(page, many=True).data
            )
        return Response(DirectMessageSerializer(messages, many=True).data)

    @action(detail=False, methods=["get"], url_path="inbox")
    def inbox(self, request):
        """Latest message per conversation partner."""
        from django.db.models import Q, Count
        user = request.user
        messages = DirectMessage.objects.filter(
            Q(sender=user) | Q(recipient=user)
        ).order_by("-sent_at")

        # Single query for unread counts per sender (avoids N+1 per partner)
        unread_counts = DirectMessage.objects.filter(
            recipient=user, status__in=["sent", "delivered"]
        ).values("sender").annotate(count=Count("id"))
        unread_map = {
            str(item["sender"]): item["count"] for item in unread_counts
        }

        seen_partners = set()
        threads = []
        for msg in messages:
            partner = msg.recipient if msg.sender == user else msg.sender
            if partner.id not in seen_partners:
                seen_partners.add(partner.id)
                threads.append({
                    "partner": {
                        "id": str(partner.id),
                        "name": partner.full_name,
                        "role": partner.role,
                        "avatar": partner.avatar.url if partner.avatar else None,
                    },
                    "last_message": DirectMessageSerializer(msg).data,
                    "unread_count": unread_map.get(str(partner.id), 0),
                })
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
        count = Notification.objects.filter(
            user=request.user, read_at__isnull=True
        ).update(status="read", read_at=timezone.now())
        return Response({"marked_read": count})

    @action(detail=False, methods=["get"], url_path="unread-count")
    def unread_count(self, request):
        count = Notification.objects.filter(
            user=request.user, channel="in_app", read_at__isnull=True
        ).count()
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
        updated = DeviceToken.objects.filter(
            user=request.user, token=pk
        ).update(is_active=False)
        if updated:
            return Response({"detail": "Token deactivated."})
        return Response(
            {"detail": "Token not found."},
            status=status.HTTP_404_NOT_FOUND,
        )
