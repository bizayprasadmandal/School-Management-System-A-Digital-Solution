"""Debug tests — verify DirectMessageViewSet endpoints work correctly."""
import pytest
import json


pytestmark = pytest.mark.django_db


class TestMessagesAPI:
    """Verify the DirectMessage endpoints return correct responses."""

    def test_message_list(self, api_client, user):
        """GET /messages/ should return 200 for authenticated users."""
        resp = api_client.get("/api/v1/communication/messages/")
        assert resp.status_code == 200

    def test_message_inbox(self, api_client, user):
        """GET /messages/inbox/ should return 200 for authenticated users."""
        resp = api_client.get("/api/v1/communication/messages/inbox/")
        assert resp.status_code == 200

    def test_message_conversation(self, api_client, user):
        """GET /messages/conversation/{id}/ should handle nonexistent id."""
        resp = api_client.get(
            f"/api/v1/communication/messages/conversation/{user.id}/"
        )
        # Should either return 200 (empty list) or 404
        assert resp.status_code in (200, 404)
