"""
WebSocket URL patterns for Django Channels
"""

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(
        r"^ws/chat/(?P<recipient_id>[0-9a-f-]+)/$",
        consumers.ChatConsumer.as_asgi(),
    ),
    re_path(
        r"^ws/notifications/$",
        consumers.NotificationConsumer.as_asgi(),
    ),
    re_path(
        r"^ws/attendance/(?P<classroom_id>\d+)/(?P<date>\d{4}-\d{2}-\d{2})/$",
        consumers.AttendanceLiveConsumer.as_asgi(),
    ),
]
