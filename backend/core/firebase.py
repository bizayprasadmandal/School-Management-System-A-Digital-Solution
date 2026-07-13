"""
Firebase Cloud Messaging — lazy initialization.

Initializes the Firebase Admin SDK on first use so that the app can
start up even when Firebase credentials are not configured (e.g. in
development or test environments). Tasks that attempt to send a push
notification will log a warning and skip if no credentials are set.
"""

import json
import logging

from django.conf import settings

logger = logging.getLogger(__name__)

_firebase_available = False  # True only after successful init
_firebase_attempted = False  # True after first init attempt (success or failure)


def get_firebase_app():
    """
    Return the (lazily-initialized) Firebase app instance.
    Returns None if Firebase is not configured or init failed.
    """
    global _firebase_available, _firebase_attempted

    if _firebase_attempted:
        if _firebase_available:
            import firebase_admin
            return firebase_admin.get_app()
        return None

    _firebase_attempted = True

    creds_raw = settings.FIREBASE_CREDENTIALS
    if not creds_raw:
        logger.warning(
            "FIREBASE_CREDENTIALS not configured — push notifications disabled"
        )
        return None

    try:
        import firebase_admin
        from firebase_admin import credentials

        # Support both JSON string and file-path formats
        try:
            creds_dict = json.loads(creds_raw)
            cred = credentials.Certificate(creds_dict)
        except json.JSONDecodeError:
            cred = credentials.Certificate(creds_raw)

        firebase_admin.initialize_app(cred)
        _firebase_available = True
        logger.info("Firebase Admin SDK initialized successfully")
        return firebase_admin.get_app()

    except Exception as exc:
        logger.error("Failed to initialize Firebase: %s", exc)
        return None
