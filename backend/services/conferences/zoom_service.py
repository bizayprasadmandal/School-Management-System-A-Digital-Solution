"""
Zoom Server-to-Server OAuth Service
====================================
Uses Zoom's new OAuth flow with Account ID, Client ID, and Client Secret.
Zoom deprecated API Key / API Secret — this implementation uses the
`grant_type=account_credentials` flow.

Docs: https://developers.zoom.us/docs/internal-apps/s2s-oauth/
"""

import base64
import logging
from datetime import datetime, timedelta
from typing import Any

import requests
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

ZOOM_TOKEN_URL = "https://zoom.us/oauth/token"
ZOOM_API_BASE = "https://api.zoom.us/v2"
CACHE_KEY_TOKEN = "zoom_access_token"
TOKEN_EXPIRY_BUFFER = 60  # seconds before expiry to consider token stale


# ─── Token Management ─────────────────────────────────────────────────────────


def _get_client_credentials() -> tuple[str, str, str] | None:
    """Return (account_id, client_id, client_secret) or None if not configured."""
    account_id = getattr(settings, "ZOOM_ACCOUNT_ID", "")
    client_id = getattr(settings, "ZOOM_CLIENT_ID", "")
    client_secret = getattr(settings, "ZOOM_CLIENT_SECRET", "")
    if not account_id or not client_id or not client_secret:
        return None
    return account_id, client_id, client_secret


def _basic_auth_header(client_id: str, client_secret: str) -> str:
    """Base64-encode client_id:client_secret for Basic auth."""
    raw = f"{client_id}:{client_secret}"
    encoded = base64.b64encode(raw.encode()).decode()
    return f"Basic {encoded}"


def request_access_token() -> dict[str, Any] | None:
    """
    Request a fresh access token from Zoom using account_credentials grant.
    Returns the full response dict (access_token, expires_in, scope) or None.
    """
    creds = _get_client_credentials()
    if not creds:
        logger.warning("Zoom credentials not configured — cannot request token")
        return None

    account_id, client_id, client_secret = creds

    headers = {
        "Authorization": _basic_auth_header(client_id, client_secret),
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "grant_type": "account_credentials",
        "account_id": account_id,
    }

    try:
        resp = requests.post(ZOOM_TOKEN_URL, headers=headers, data=data, timeout=10)
        resp.raise_for_status()
        token_data = resp.json()
        logger.info("Zoom access token obtained successfully")
        return token_data
    except requests.RequestException as e:
        logger.error("Failed to obtain Zoom access token: %s", e)
        return None


def get_access_token() -> str | None:
    """
    Get a valid Zoom access token — from cache if available and not near expiry,
    otherwise request a fresh one.
    Returns the token string or None if Zoom is not configured.
    """
    creds = _get_client_credentials()
    if not creds:
        return None

    # Check cache
    cached: dict | None = cache.get(CACHE_KEY_TOKEN)
    if cached:
        expires_at = cached.get("expires_at")
        if expires_at and datetime.utcnow().timestamp() < expires_at:
            return cached["access_token"]

    # Request fresh token
    token_data = request_access_token()
    if not token_data:
        return None

    access_token = token_data.get("access_token")
    expires_in = token_data.get("expires_in", 3600)  # default 1 hour

    # Cache token, refreshing a bit early to avoid edge cases
    cache.set(
        CACHE_KEY_TOKEN,
        {
            "access_token": access_token,
            "expires_at": datetime.utcnow().timestamp() + expires_in - TOKEN_EXPIRY_BUFFER,
        },
        timeout=expires_in - TOKEN_EXPIRY_BUFFER,
    )

    return access_token


# ─── API Client ────────────────────────────────────────────────────────────────


def _api_headers() -> dict[str, str]:
    """Build common API headers with Bearer token."""
    token = get_access_token()
    if not token:
        raise ValueError("Zoom is not configured — missing credentials")
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


def get_user(user_id: str = "me") -> dict[str, Any] | None:
    """
    Get Zoom user info. Use 'me' for the account owner.
    Returns the user object or None on failure.
    """
    try:
        resp = requests.get(
            f"{ZOOM_API_BASE}/users/{user_id}",
            headers=_api_headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.error("Zoom get_user failed: %s", e)
        return None


def create_meeting(
    topic: str,
    start_time: str,          # ISO 8601, e.g. "2025-06-15T15:00:00Z"
    duration_minutes: int = 30,
    password: str | None = None,
    settings: dict | None = None,
    user_id: str = "me",
) -> dict[str, Any] | None:
    """
    Create a Zoom meeting.
    Returns the meeting object (id, join_url, start_url, password, etc.) or None.
    """
    payload: dict[str, Any] = {
        "topic": topic,
        "type": 2,  # Scheduled meeting
        "start_time": start_time,
        "duration": duration_minutes,
        "timezone": "UTC",
        "settings": settings or {
            "host_video": True,
            "participant_video": True,
            "join_before_host": False,
            "mute_upon_entry": True,
            "waiting_room": True,
            "approval_type": 0,  # Automatically approve
            "registration_type": 1,  # Attendees register once
            "auto_recording": "none",
        },
    }
    if password:
        payload["password"] = password

    try:
        resp = requests.post(
            f"{ZOOM_API_BASE}/users/{user_id}/meetings",
            headers=_api_headers(),
            json=payload,
            timeout=10,
        )
        resp.raise_for_status()
        meeting = resp.json()
        logger.info("Zoom meeting created: %s (id=%s)", topic, meeting.get("id"))
        return meeting
    except Exception as e:
        logger.error("Zoom create_meeting failed: %s", e)
        if hasattr(e, "response") and e.response is not None:
            logger.error("Response: %s", e.response.text)
        return None


def list_meetings(user_id: str = "me", page_size: int = 30) -> list[dict[str, Any]]:
    """List upcoming meetings for a Zoom user."""
    try:
        resp = requests.get(
            f"{ZOOM_API_BASE}/users/{user_id}/meetings",
            headers=_api_headers(),
            params={"type": "upcoming", "page_size": page_size},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("meetings", [])
    except Exception as e:
        logger.error("Zoom list_meetings failed: %s", e)
        return []


def get_meeting(meeting_id: int | str) -> dict[str, Any] | None:
    """Get a specific meeting by ID."""
    try:
        resp = requests.get(
            f"{ZOOM_API_BASE}/meetings/{meeting_id}",
            headers=_api_headers(),
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.error("Zoom get_meeting failed: %s", e)
        return None


def update_meeting(
    meeting_id: int | str,
    payload: dict[str, Any],
) -> bool:
    """Update a meeting. Returns True on success."""
    try:
        resp = requests.patch(
            f"{ZOOM_API_BASE}/meetings/{meeting_id}",
            headers=_api_headers(),
            json=payload,
            timeout=10,
        )
        resp.raise_for_status()
        logger.info("Zoom meeting %s updated", meeting_id)
        return True
    except Exception as e:
        logger.error("Zoom update_meeting failed: %s", e)
        return False


def delete_meeting(meeting_id: int | str) -> bool:
    """Delete a meeting. Returns True on success."""
    try:
        resp = requests.delete(
            f"{ZOOM_API_BASE}/meetings/{meeting_id}",
            headers=_api_headers(),
            timeout=10,
        )
        if resp.status_code == 204:
            logger.info("Zoom meeting %s deleted", meeting_id)
            return True
        resp.raise_for_status()
        return True
    except Exception as e:
        logger.error("Zoom delete_meeting failed: %s", e)
        return False


# ─── Health / Connection Check ────────────────────────────────────────────────


def check_connection() -> dict[str, Any]:
    """
    Test Zoom connection by requesting a token and fetching user info.
    Returns a dict with status, detail, and optionally user info.
    """
    token = get_access_token()
    if not token:
        return {"status": "error", "detail": "Failed to obtain access token"}

    user = get_user("me")
    if not user:
        return {"status": "error", "detail": "Token obtained but failed to fetch user info"}

    return {
        "status": "connected",
        "detail": "Successfully connected to Zoom API",
        "user": {
            "id": user.get("id"),
            "email": user.get("email"),
            "display_name": user.get("first_name", "") + " " + user.get("last_name", ""),
        },
    }
