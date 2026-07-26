"""Tests for Communication Service — Announcements, Notifications, DirectMessages."""

import pytest
from rest_framework import status
from rest_framework.test import APIClient
from tests.url_helpers import (
    COMMUNICATION_ANNOUNCEMENTS, COMMUNICATION_NOTIFICATIONS,
    COMMUNICATION_NOTIFICATIONS_UNREAD_COUNT,
    COMMUNICATION_NOTIFICATIONS_MARK_ALL_READ,
    COMMUNICATION_MESSAGES,
    communication_announcement_detail,
    communication_announcement_publish,
    communication_announcement_mark_read,
)
from django.utils import timezone


# ─── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def school(db):
    from tests.factories import SchoolFactory
    return SchoolFactory()


@pytest.fixture
def admin_user(db, school):
    from tests.factories import AdminUserFactory
    return AdminUserFactory(school=school)


@pytest.fixture
def teacher_user(db, school):
    from tests.factories import TeacherUserFactory
    return TeacherUserFactory(school=school)


@pytest.fixture
def student_user(db, school):
    from tests.factories import StudentUserFactory
    return StudentUserFactory(school=school)


@pytest.fixture
def other_user(db, school):
    from tests.factories import UserFactory
    return UserFactory(school=school, email="other@school.edu")


@pytest.fixture
def admin_auth_client(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def teacher_auth_client(api_client, teacher_user):
    api_client.force_authenticate(user=teacher_user)
    return api_client


@pytest.fixture
def student_auth_client(api_client, student_user):
    api_client.force_authenticate(user=student_user)
    return api_client


@pytest.fixture
def other_auth_client(api_client, other_user):
    api_client.force_authenticate(user=other_user)
    return api_client


# ─── Announcement Tests ──────────────────────────────────────────────────────

@pytest.mark.django_db
class TestAnnouncements:

    def test_admin_can_create_announcement(self, admin_auth_client):
        payload = {
            "title": "School Closed",
            "content": "School will be closed on Monday.",
            "priority": "high",
            "audience": "all",
        }
        response = admin_auth_client.post(COMMUNICATION_ANNOUNCEMENTS, payload, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["title"] == "School Closed"
        # Draft by default (is_draft not set)
        assert response.data["is_draft"] is True

    def test_student_cannot_create_announcement(self, student_auth_client):
        payload = {"title": "Test", "content": "Test content", "priority": "normal", "audience": "all"}
        response = student_auth_client.post(COMMUNICATION_ANNOUNCEMENTS, payload, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_can_publish_announcement(self, admin_auth_client, school):
        from tests.factories import AnnouncementFactory
        ann = AnnouncementFactory(school=school, is_draft=True)
        response = admin_auth_client.post(
            communication_announcement_publish(ann.id),
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert "published" in response.data["detail"].lower()

    def test_publish_twice_returns_400(self, admin_auth_client, school):
        from tests.factories import AnnouncementFactory
        ann = AnnouncementFactory(
            school=school,
            is_draft=False, published_at=timezone.now(),
        )
        response = admin_auth_client.post(
            communication_announcement_publish(ann.id),
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_mark_announcement_read(self, admin_auth_client, school):
        from tests.factories import AnnouncementFactory
        ann = AnnouncementFactory(
            school=school,
            is_draft=False, published_at=timezone.now(),
        )
        initial_views = ann.view_count
        response = admin_auth_client.post(
            communication_announcement_mark_read(ann.id),
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        ann.refresh_from_db()
        assert ann.view_count == initial_views + 1

    def test_student_sees_only_published_announcements(self, student_auth_client, school):
        from tests.factories import AnnouncementFactory
        AnnouncementFactory(
            school=school, is_draft=True,
            title="Draft Title",
        )
        AnnouncementFactory(
            school=school, is_draft=False, published_at=timezone.now(),
            title="Published Title",
        )
        response = student_auth_client.get(COMMUNICATION_ANNOUNCEMENTS)
        assert response.status_code == status.HTTP_200_OK
        titles = [a["title"] for a in response.data["results"]]
        assert "Published Title" in titles
        assert "Draft Title" not in titles

    def test_announcement_audience_filter(self, admin_auth_client, school):
        from tests.factories import AnnouncementFactory
        AnnouncementFactory(
            school=school, audience="teachers", title="Teacher Only",
            is_draft=False, published_at=timezone.now(),
        )
        AnnouncementFactory(
            school=school, audience="students", title="Student Only",
            is_draft=False, published_at=timezone.now(),
        )
        response = admin_auth_client.get(COMMUNICATION_ANNOUNCEMENTS)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] >= 2

    def test_tenant_isolation_announcement(self, db):
        """School A cannot see School B announcements."""
        from tests.factories import SchoolFactory, AdminUserFactory, AnnouncementFactory
        school_a = SchoolFactory(code="ANNA")
        school_b = SchoolFactory(code="ANNB")
        admin_a = AdminUserFactory(school=school_a)
        AnnouncementFactory(
            school=school_b, title="Secret",
            is_draft=False, published_at=timezone.now(),
        )
        client = APIClient()
        client.force_authenticate(user=admin_a)
        response = client.get(COMMUNICATION_ANNOUNCEMENTS)
        titles = [a["title"] for a in response.data["results"]]
        assert "Secret" not in titles


# ─── Notification Tests ──────────────────────────────────────────────────────

@pytest.mark.django_db
class TestNotifications:

    def test_list_notifications(self, student_auth_client, student_user):
        from tests.factories import NotificationFactory
        NotificationFactory(user=student_user, title="Test Notification")
        response = student_auth_client.get(COMMUNICATION_NOTIFICATIONS)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] >= 1

    def test_notification_isolation(self, admin_auth_client, student_user):
        """Admin should not see student's notifications (different users)."""
        from tests.factories import NotificationFactory
        NotificationFactory(user=student_user, title="Student Nudge")
        response = admin_auth_client.get(COMMUNICATION_NOTIFICATIONS)
        titles = [n["title"] for n in response.data["results"]]
        assert "Student Nudge" not in titles

    def test_unread_count(self, student_auth_client, student_user):
        from tests.factories import NotificationFactory
        NotificationFactory(user=student_user, title="Unread One", read_at=None)
        NotificationFactory(user=student_user, title="Read One", read_at=timezone.now())
        response = student_auth_client.get(COMMUNICATION_NOTIFICATIONS_UNREAD_COUNT)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] >= 1

    def test_mark_notification_read(self, student_auth_client, student_user):
        from tests.factories import NotificationFactory
        notif = NotificationFactory(user=student_user, title="Unread")
        response = student_auth_client.patch(
            f"{COMMUNICATION_NOTIFICATIONS}{notif.id}/mark-read/",
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        notif.refresh_from_db()
        assert notif.read_at is not None

    def test_mark_all_read(self, student_auth_client, student_user):
        from tests.factories import NotificationFactory
        NotificationFactory(user=student_user, title="A", read_at=None)
        NotificationFactory(user=student_user, title="B", read_at=None)
        response = student_auth_client.post(
            COMMUNICATION_NOTIFICATIONS_MARK_ALL_READ,
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["marked_read"] >= 2

    def test_notification_filter_by_channel(self, student_auth_client, student_user):
        from tests.factories import NotificationFactory
        NotificationFactory(user=student_user, channel="in_app")
        NotificationFactory(user=student_user, channel="email")
        response = student_auth_client.get(f"{COMMUNICATION_NOTIFICATIONS}?channel=email")
        assert response.status_code == status.HTTP_200_OK
        for n in response.data["results"]:
            assert n["channel"] == "email"

    def test_notification_ordering(self, student_auth_client, student_user):
        from tests.factories import NotificationFactory
        NotificationFactory(user=student_user, title="Older")
        import time as time_module
        time_module.sleep(0.01)
        NotificationFactory(user=student_user, title="Newer")
        response = student_auth_client.get(COMMUNICATION_NOTIFICATIONS)
        titles = [n["title"] for n in response.data["results"]]
        assert titles.index("Newer") < titles.index("Older")


# ─── DirectMessage Tests ─────────────────────────────────────────────────────

@pytest.mark.django_db
class TestDirectMessages:

    def test_send_message(self, other_auth_client, student_user):
        payload = {"recipient": student_user.id, "content": "Hello there!"}
        response = other_auth_client.post(COMMUNICATION_MESSAGES, payload, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["content"] == "Hello there!"

    def test_cannot_message_self(self, other_auth_client):
        user = other_auth_client.handler._force_user
        payload = {"recipient": user.id, "content": "Hi me"}
        response = other_auth_client.post(COMMUNICATION_MESSAGES, payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_cannot_message_other_school(self, other_auth_client, student_user):
        """Users from different schools cannot message each other (serializer validation)."""
        from tests.factories import SchoolFactory, UserFactory
        other_school = SchoolFactory(code="MSGOS")
        other_user = UserFactory(school=other_school)
        payload = {"recipient": other_user.id, "content": "Cross-school message"}
        response = other_auth_client.post(COMMUNICATION_MESSAGES, payload, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_get_conversation(self, other_auth_client, student_user):
        from tests.factories import DirectMessageFactory
        sender = other_auth_client.handler._force_user
        # Message from sender to student
        DirectMessageFactory(sender=sender, recipient=student_user, content="Hello")
        # Message from student to sender
        DirectMessageFactory(sender=student_user, recipient=sender, content="Hi back")
        response = other_auth_client.get(
            f"{COMMUNICATION_MESSAGES}conversation/{student_user.id}/"
        )
        assert response.status_code == status.HTTP_200_OK
        contents = [m["content"] for m in response.data["results"]]
        assert "Hello" in contents
        assert "Hi back" in contents

    def test_inbox_returns_threads(self, other_auth_client, student_user):
        from tests.factories import DirectMessageFactory
        sender = other_auth_client.handler._force_user
        DirectMessageFactory(sender=sender, recipient=student_user, content="Last msg")
        response = other_auth_client.get(f"{COMMUNICATION_MESSAGES}inbox/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
        assert response.data[0]["last_message"]["content"] == "Last msg"

    def test_inbox_unread_count(self, other_auth_client, student_user):
        from tests.factories import DirectMessageFactory
        sender = other_auth_client.handler._force_user
        DirectMessageFactory(
            sender=student_user, recipient=sender,
            content="Unread", status="sent",
        )
        response = other_auth_client.get(f"{COMMUNICATION_MESSAGES}inbox/")
        assert response.status_code == status.HTTP_200_OK
        unread = sum(
            t["unread_count"] for t in response.data
            if t["partner"]["id"] == str(student_user.id)
        )
        assert unread >= 1

    def test_message_tenant_isolation(self, db):
        """School A cannot see School B messages."""
        from tests.factories import SchoolFactory, UserFactory, DirectMessageFactory
        school_a = SchoolFactory(code="MSGA")
        school_b = SchoolFactory(code="MSGB")
        user_a = UserFactory(school=school_a)
        user_b = UserFactory(school=school_b)
        DirectMessageFactory(sender=user_b, recipient=user_b, content="Secret msg")

        client = APIClient()
        client.force_authenticate(user=user_a)
        response = client.get(COMMUNICATION_MESSAGES)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 0
