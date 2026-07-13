"""
Test Suite — Email Verification Flow

Covers sending verification emails, confirming tokens, and middleware enforcement
of the email_verified field.  Follows the same patterns as test_2fa.py.
"""

import secrets
from datetime import timedelta

import pytest
from django.core import mail
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from services.auth.models import EmailVerificationToken
from tests.factories import SchoolFactory, UserFactory
from tests.url_helpers import (
    AUTH_LOGIN,
    AUTH_ME,
    AUTH_SEND_VERIFICATION,
    AUTH_CONFIRM_VERIFICATION,
    AUTH_PASSWORD_RESET,
    AUTH_PASSWORD_RESET_CONFIRM,
    STUDENTS_LIST,
)


# ─── Fixtures ─────────────────────────────────────────────────────────────────


@pytest.fixture
def school(db):
    return SchoolFactory()


@pytest.fixture
def unverified_user(db, school):
    """User with email_verified=False."""
    return UserFactory(
        school=school,
        email="unverified@school.edu",
        role="student",
        email_verified=False,
    )


@pytest.fixture
def verified_user(db, school):
    """User with email_verified=True (default from factory)."""
    return UserFactory(
        school=school,
        email="verified@school.edu",
        role="student",
    )


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def unverified_client(db, unverified_user):
    client = APIClient()
    client.force_authenticate(user=unverified_user)
    return client, unverified_user


@pytest.fixture
def verified_client(db, verified_user):
    client = APIClient()
    client.force_authenticate(user=verified_user)
    return client, verified_user


def _create_verification_token(user, email=None, hours_from_now=24):
    """Helper to create a valid EmailVerificationToken in the DB."""
    token_str = secrets.token_urlsafe(48)
    return EmailVerificationToken.objects.create(
        user=user,
        email=email or user.email,
        token=token_str,
        expires_at=timezone.now() + timedelta(hours=hours_from_now),
        used=False,
    )


# ─── Send Verification Email Tests ────────────────────────────────────────────


@pytest.mark.django_db
class TestSendVerificationEmail:

    def test_send_creates_token_and_sends_email(self, unverified_client):
        """Authenticated unverified user receives a verification email."""
        client, user = unverified_client
        r = client.post(AUTH_SEND_VERIFICATION)

        assert r.status_code == status.HTTP_200_OK
        assert "sent" in r.data["detail"].lower()

        # Check email was sent via locmem backend
        assert len(mail.outbox) == 1
        assert mail.outbox[0].to == [user.email]
        assert "Verify Your Email" in mail.outbox[0].subject
        assert user.email in mail.outbox[0].body

        # Check token was created in DB
        token_count = EmailVerificationToken.objects.filter(
            user=user, used=False
        ).count()
        assert token_count == 1

        # Verify the email body contains the token
        token = EmailVerificationToken.objects.get(user=user, used=False)
        assert token.token in mail.outbox[0].body

    def test_send_requires_authentication(self, api_client):
        """Unauthenticated request returns 401."""
        r = api_client.post(AUTH_SEND_VERIFICATION)
        assert r.status_code == status.HTTP_401_UNAUTHORIZED

    def test_send_when_already_verified(self, verified_client):
        """User with email_verified=True gets a validation error."""
        client, user = verified_client
        r = client.post(AUTH_SEND_VERIFICATION)
        assert r.status_code == status.HTTP_400_BAD_REQUEST
        assert "already verified" in r.data["email"][0].lower()

    def test_send_invalidates_old_tokens(self, unverified_client):
        """Previous unused tokens are invalidated when a new one is created."""
        client, user = unverified_client

        # Create two old tokens
        old_token1 = _create_verification_token(user)
        old_token2 = _create_verification_token(user)

        # Send new verification
        r = client.post(AUTH_SEND_VERIFICATION)
        assert r.status_code == status.HTTP_200_OK

        # Old tokens should now be marked as used
        old_token1.refresh_from_db()
        old_token2.refresh_from_db()
        assert old_token1.used is True
        assert old_token2.used is True

        # Only the new token should be unused
        assert EmailVerificationToken.objects.filter(user=user, used=False).count() == 1

    def test_send_accepts_optional_email_field(self, unverified_client):
        """Explicitly passing the same email works."""
        client, user = unverified_client
        r = client.post(AUTH_SEND_VERIFICATION, {"email": user.email})
        assert r.status_code == status.HTTP_200_OK

    def test_send_rejects_different_email(self, unverified_client):
        """Cannot request verification for a different email address."""
        client, user = unverified_client
        r = client.post(AUTH_SEND_VERIFICATION, {"email": "other@school.edu"})
        assert r.status_code == status.HTTP_400_BAD_REQUEST
        assert "own email" in r.data["email"][0].lower()

    def test_send_accepts_custom_verification_base_url(self, unverified_client):
        """Custom verification base URL is used in the email."""
        client, user = unverified_client
        custom_url = "https://myapp.com/auth"
        r = client.post(AUTH_SEND_VERIFICATION, {
            "verification_base_url": custom_url,
        })
        assert r.status_code == status.HTTP_200_OK
        assert custom_url in mail.outbox[0].body

    def test_send_audit_log_created(self, unverified_client):
        """An audit log entry is created for the send action."""
        from services.auth.models import AuditLog
        client, user = unverified_client
        client.post(AUTH_SEND_VERIFICATION)
        assert AuditLog.objects.filter(
            user=user, action="send_verification_email"
        ).exists()


# ─── Confirm Email Verification Tests ─────────────────────────────────────────


@pytest.mark.django_db
class TestConfirmEmailVerification:

    def test_confirm_sets_email_verified(self, unverified_client):
        """Valid token marks the user's email as verified."""
        client, user = unverified_client
        token = _create_verification_token(user)

        r = client.post(AUTH_CONFIRM_VERIFICATION, {"token": token.token})
        assert r.status_code == status.HTTP_200_OK
        assert r.data["email_verified"] is True

        user.refresh_from_db()
        assert user.email_verified is True

        # Token should be marked as used
        token.refresh_from_db()
        assert token.used is True

    def test_confirm_works_unauthenticated(self, api_client, unverified_user):
        """AllowAny — verifying via email link (no auth header) works."""
        token = _create_verification_token(unverified_user)
        r = api_client.post(AUTH_CONFIRM_VERIFICATION, {"token": token.token})
        assert r.status_code == status.HTTP_200_OK
        assert r.data["email_verified"] is True

    def test_confirm_invalid_token(self, unverified_client):
        """Non-existent token returns 400."""
        client, user = unverified_client
        r = client.post(AUTH_CONFIRM_VERIFICATION, {
            "token": "totally-fake-token-that-does-not-exist",
        })
        assert r.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid" in r.data["detail"]

    def test_confirm_expired_token(self, unverified_client):
        """Expired token returns 400 with a clear message."""
        client, user = unverified_client
        # Create a token that expired 1 hour ago
        token = _create_verification_token(user, hours_from_now=-1)

        r = client.post(AUTH_CONFIRM_VERIFICATION, {"token": token.token})
        assert r.status_code == status.HTTP_400_BAD_REQUEST
        assert "expired" in r.data["detail"].lower()

    def test_confirm_already_used_token(self, unverified_client):
        """Already used token returns 400."""
        client, user = unverified_client
        token = _create_verification_token(user)
        token.used = True
        token.save(update_fields=["used"])

        r = client.post(AUTH_CONFIRM_VERIFICATION, {"token": token.token})
        assert r.status_code == status.HTTP_400_BAD_REQUEST
        assert "used" in r.data["detail"].lower() or "Invalid" in r.data["detail"]

    def test_confirm_updates_email_if_changed(self, unverified_client):
        """Token can carry a different email and the user's email gets updated."""
        client, user = unverified_client
        new_email = "updated-email@school.edu"
        token = _create_verification_token(user, email=new_email)

        r = client.post(AUTH_CONFIRM_VERIFICATION, {"token": token.token})
        assert r.status_code == status.HTTP_200_OK

        user.refresh_from_db()
        assert user.email == new_email
        assert user.email_verified is True

    def test_confirm_rejects_token_for_other_user(self, api_client, db, school):
        """An authenticated user cannot use another user's verification token."""
        user_a = UserFactory(school=school, email="alice@school.edu", email_verified=False)
        user_b = UserFactory(school=school, email="bob@school.edu", email_verified=False)

        token_for_b = _create_verification_token(user_b)

        client_a = APIClient()
        client_a.force_authenticate(user=user_a)
        r = client_a.post(AUTH_CONFIRM_VERIFICATION, {"token": token_for_b.token})
        assert r.status_code == status.HTTP_403_FORBIDDEN
        assert "belongs to another user" in r.data["detail"].lower()

    def test_confirm_requires_token_field(self, unverified_client):
        """Missing token field returns 400."""
        client, user = unverified_client
        r = client.post(AUTH_CONFIRM_VERIFICATION, {})
        assert r.status_code == status.HTTP_400_BAD_REQUEST

    def test_confirm_audit_log_created(self, unverified_client):
        """An audit log entry is created for the confirm action."""
        from services.auth.models import AuditLog
        client, user = unverified_client
        token = _create_verification_token(user)
        client.post(AUTH_CONFIRM_VERIFICATION, {"token": token.token})
        assert AuditLog.objects.filter(
            user=user, action="confirm_email_verification"
        ).exists()

    def test_confirm_after_email_already_verified(self, unverified_client):
        """Confirming after already being verified still succeeds (idempotent token usage)."""
        client, user = unverified_client
        token = _create_verification_token(user)

        # First confirmation
        r1 = client.post(AUTH_CONFIRM_VERIFICATION, {"token": token.token})
        assert r1.status_code == status.HTTP_200_OK

        # Second confirmation with same token — should fail (used)
        r2 = client.post(AUTH_CONFIRM_VERIFICATION, {"token": token.token})
        assert r2.status_code == status.HTTP_400_BAD_REQUEST


# ─── Email Verification Middleware Tests ──────────────────────────────────────


@pytest.mark.django_db
class TestEmailVerificationMiddleware:

    def test_unverified_user_blocked_from_protected_endpoint(self, unverified_client):
        """
        User with email_verified=False gets 403 when accessing a protected
        endpoint (e.g., students list) when enforcement is enabled.
        """
        from django.test.utils import override_settings

        client, user = unverified_client
        with override_settings(EMAIL_VERIFICATION_ENFORCED=True):
            r = client.get(STUDENTS_LIST)
            assert r.status_code == status.HTTP_403_FORBIDDEN
            assert r.data["code"] == "email_not_verified"
            assert r.data["email_verified"] is False

    def test_unverified_user_allowed_on_auth_me(self, unverified_client):
        """
        Auth/verification whitelisted endpoints are accessible even when
        email is not verified.
        """
        from django.test.utils import override_settings

        client, user = unverified_client
        with override_settings(EMAIL_VERIFICATION_ENFORCED=True):
            r = client.get(AUTH_ME)
            assert r.status_code == status.HTTP_200_OK
            assert r.data["email_verified"] is False

    def test_unverified_user_allowed_send_verification(self, unverified_client):
        """
        The send-verification endpoint itself is accessible even when
        email is not verified (otherwise the user would be locked out).
        """
        from django.test.utils import override_settings

        client, user = unverified_client
        with override_settings(EMAIL_VERIFICATION_ENFORCED=True):
            r = client.post(AUTH_SEND_VERIFICATION)
            assert r.status_code == status.HTTP_200_OK

    def test_verified_user_not_blocked(self, verified_client):
        """
        User with email_verified=True can access protected endpoints
        normally when enforcement is enabled.
        """
        from django.test.utils import override_settings

        client, user = verified_client
        with override_settings(EMAIL_VERIFICATION_ENFORCED=True):
            r = client.get(STUDENTS_LIST)
            assert r.status_code == status.HTTP_200_OK

    def test_enforcement_off_by_default(self, unverified_client):
        """
        When EMAIL_VERIFICATION_ENFORCED is not set (or is False), unverified
        users can access all endpoints normally.
        """
        from django.test.utils import override_settings

        client, user = unverified_client
        # Explicitly set enforcement off
        with override_settings(EMAIL_VERIFICATION_ENFORCED=False):
            r = client.get(STUDENTS_LIST)
            assert r.status_code == status.HTTP_200_OK

    def test_bypass_path_allowed(self, unverified_client):
        """
        Bypass paths like /health/ are accessible even without auth
        and without email verification.
        """
        from django.test.utils import override_settings

        client, user = unverified_client
        with override_settings(EMAIL_VERIFICATION_ENFORCED=True):
            r = client.get("/health/ready/")
            # health endpoint may 404 if not configured in test, but should not 403
            assert r.status_code != status.HTTP_403_FORBIDDEN

    def test_unverified_blocked_students_list(self, unverified_client):
        """Verify the /students/ endpoint is properly blocked."""
        from django.test.utils import override_settings

        client, user = unverified_client
        with override_settings(EMAIL_VERIFICATION_ENFORCED=True):
            r = client.get(STUDENTS_LIST)
            assert r.status_code == status.HTTP_403_FORBIDDEN

    def test_complete_verification_unblocks_user(self, api_client, unverified_user):
        """
        End-to-end: unverified user is blocked → verifies email →
        is no longer blocked.
        """
        from django.test.utils import override_settings

        client = APIClient()
        client.force_authenticate(user=unverified_user)

        # Step 1: User is blocked from protected endpoint
        with override_settings(EMAIL_VERIFICATION_ENFORCED=True):
            r = client.get(STUDENTS_LIST)
            assert r.status_code == status.HTTP_403_FORBIDDEN

        # Step 2: Send verification
        r = client.post(AUTH_SEND_VERIFICATION)
        assert r.status_code == status.HTTP_200_OK
        token = EmailVerificationToken.objects.get(user=unverified_user, used=False)

        # Step 3: Confirm verification
        r = client.post(AUTH_CONFIRM_VERIFICATION, {"token": token.token})
        assert r.status_code == status.HTTP_200_OK

        # Step 4: User is no longer blocked
        unverified_user.refresh_from_db()
        assert unverified_user.email_verified is True
        with override_settings(EMAIL_VERIFICATION_ENFORCED=True):
            r = client.get(STUDENTS_LIST)
            assert r.status_code == status.HTTP_200_OK


# ─── Model / Cleanup Task Tests ───────────────────────────────────────────────


@pytest.mark.django_db
class TestEmailVerificationTokenModel:

    def test_token_is_expired_property(self, unverified_user):
        """is_expired returns True for tokens past their expiration."""
        expired_token = _create_verification_token(unverified_user, hours_from_now=-1)
        assert expired_token.is_expired is True

    def test_token_is_not_expired_for_future(self, unverified_user):
        """is_expired returns False for tokens in the future."""
        valid_token = _create_verification_token(unverified_user, hours_from_now=24)
        assert valid_token.is_expired is False

    def test_token_string_representation(self, unverified_user):
        """__str__ shows email and status."""
        token = _create_verification_token(unverified_user)
        assert str(token) == f"Verification for {unverified_user.email} — pending"
        token.used = True
        assert "used" in str(token)

    def test_cleanup_task_deletes_expired_tokens(self, unverified_user):
        """The cleanup_expired_verification_tokens task deletes expired tokens."""
        from services.auth.tasks import cleanup_expired_verification_tokens

        # Create expired tokens
        _create_verification_token(unverified_user, hours_from_now=-2)
        _create_verification_token(unverified_user, hours_from_now=-48)

        # Create a valid token — should survive cleanup
        valid = _create_verification_token(unverified_user, hours_from_now=24)

        result = cleanup_expired_verification_tokens()
        assert result["deleted"] >= 2

        remaining = EmailVerificationToken.objects.filter(user=unverified_user)
        assert remaining.count() == 1
        assert remaining.first().id == valid.id


# ─── Password Reset + Email Verification Tests ────────────────────────────────


@pytest.mark.django_db
class TestPasswordResetAndEmailVerification:
    """
    Verify that unverified users can still use the password reset flow,
    and that the password reset endpoints are whitelisted in the email
    verification middleware.
    """

    # ── Fixtures ────────────────────────────────────────────────────────────

    @pytest.fixture
    def reset_user(self, db, school):
        """A user who will request a password reset."""
        from tests.factories import UserFactory
        return UserFactory(
            school=school,
            email="reset-test@school.edu",
            role="student",
            email_verified=False,
        )

    def _request_reset(self, api_client, email: str):
        """Helper: request a password reset token."""
        return api_client.post(AUTH_PASSWORD_RESET, {"email": email})

    def _create_reset_token(self, user):
        """Helper: create a valid password reset token directly in the DB."""
        import secrets
        from services.auth.models import PasswordResetToken
        token_str = secrets.token_urlsafe(48)
        return PasswordResetToken.objects.create(
            user=user,
            token=token_str,
            expires_at=timezone.now() + timedelta(hours=2),
            used=False,
        )

    # ── Tests ────────────────────────────────────────────────────────────────

    def test_unverified_user_can_request_password_reset(self, api_client, reset_user):
        """
        An unverified user can request a password reset. The endpoint
        is AllowAny and returns success regardless of email verification status.
        """
        r = self._request_reset(api_client, reset_user.email)
        assert r.status_code == status.HTTP_200_OK
        assert "reset link" in r.data["detail"].lower()

        # Verify a PasswordResetToken was created
        from services.auth.models import PasswordResetToken
        assert PasswordResetToken.objects.filter(user=reset_user, used=False).exists()

    def test_unverified_user_can_confirm_password_reset(self, api_client, reset_user):
        """
        An unverified user can confirm a password reset. The endpoint
        is AllowAny and not blocked by email verification.
        """
        token = self._create_reset_token(reset_user)
        new_password = "NewStrongPass@789"

        r = api_client.post(AUTH_PASSWORD_RESET_CONFIRM, {
            "token": token.token,
            "new_password": new_password,
        })
        assert r.status_code == status.HTTP_200_OK
        assert "reset successfully" in r.data["detail"].lower()

        # Verify the password actually changed
        reset_user.refresh_from_db()
        assert reset_user.check_password(new_password)

        # Token should be marked as used
        token.refresh_from_db()
        assert token.used is True

        # Email should still be unverified (password reset doesn't affect this)
        assert reset_user.email_verified is False

    def test_unverified_user_can_login_with_new_password_after_reset(
        self, api_client, reset_user
    ):
        """
        After resetting their password, an unverified user can log in
        with the new credentials (email_verified is not required for login).
        """
        token = self._create_reset_token(reset_user)
        new_password = "AfterResetPass@456"

        # Confirm reset
        api_client.post(AUTH_PASSWORD_RESET_CONFIRM, {
            "token": token.token,
            "new_password": new_password,
        })

        # Login with new password
        r = api_client.post(AUTH_LOGIN, {
            "email": reset_user.email,
            "password": new_password,
        })
        assert r.status_code == status.HTTP_200_OK
        assert "access" in r.data
        assert r.data["user"]["email_verified"] is False

    def test_reset_token_invalid_after_use(self, api_client, reset_user):
        """A used reset token cannot be reused."""
        token = self._create_reset_token(reset_user)

        # First use — should succeed
        r1 = api_client.post(AUTH_PASSWORD_RESET_CONFIRM, {
            "token": token.token,
            "new_password": "NewPassAfterUse@123",
        })
        assert r1.status_code == status.HTTP_200_OK

        # Second use with same token — should fail
        r2 = api_client.post(AUTH_PASSWORD_RESET_CONFIRM, {
            "token": token.token,
            "new_password": "AnotherPass@456",
        })
        assert r2.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid" in r2.data["detail"]

    def test_expired_reset_token_rejected(self, api_client, reset_user):
        """An expired password reset token is rejected."""
        # Create a token that expired 1 hour ago
        import secrets
        from services.auth.models import PasswordResetToken
        expired_token = PasswordResetToken.objects.create(
            user=reset_user,
            token=secrets.token_urlsafe(48),
            expires_at=timezone.now() - timedelta(hours=1),
            used=False,
        )

        r = api_client.post(AUTH_PASSWORD_RESET_CONFIRM, {
            "token": expired_token.token,
            "new_password": "ExpiredPass@789",
        })
        assert r.status_code == status.HTTP_400_BAD_REQUEST
        assert "expired" in r.data["detail"].lower()

    def test_password_reset_request_returns_success_for_unknown_email(
        self, api_client
    ):
        """
        Requesting a password reset for an unknown email returns the same
        success message (don't reveal if the email exists).
        """
        r = api_client.post(AUTH_PASSWORD_RESET, {
            "email": "nonexistent-unknown@school.edu",
        })
        assert r.status_code == status.HTTP_200_OK
        assert "reset link" in r.data["detail"].lower()
        # No token should be created
        from services.auth.models import PasswordResetToken
        assert PasswordResetToken.objects.count() == 0

    def test_password_reset_allowed_when_middleware_enforced(self, api_client, reset_user):
        """
        When EMAIL_VERIFICATION_ENFORCED is True, the password reset
        endpoints are whitelisted (ALLOWED_AUTH_PATHS) so unverified
        users can still use them.
        """
        from django.test.utils import override_settings

        token = self._create_reset_token(reset_user)

        with override_settings(EMAIL_VERIFICATION_ENFORCED=True):
            # Request reset — should work
            r_req = self._request_reset(api_client, reset_user.email)
            assert r_req.status_code == status.HTTP_200_OK

            # Confirm reset — should work
            r_conf = api_client.post(AUTH_PASSWORD_RESET_CONFIRM, {
                "token": token.token,
                "new_password": "MiddlewarePass@123",
            })
            assert r_conf.status_code == status.HTTP_200_OK
            assert "reset successfully" in r_conf.data["detail"].lower()

    def test_password_reset_does_not_affect_email_verified_status(
        self, api_client, reset_user
    ):
        """
        After a password reset, the user's email_verified field remains
        unchanged (false in this case). Password reset is a separate concern.
        """
        assert reset_user.email_verified is False

        token = self._create_reset_token(reset_user)
        api_client.post(AUTH_PASSWORD_RESET_CONFIRM, {
            "token": token.token,
            "new_password": "NewPassKeepStatus@789",
        })

        reset_user.refresh_from_db()
        assert reset_user.email_verified is False  # Unchanged

    def test_request_reset_with_unverified_email_and_verification_pending(
        self, api_client, unverified_user
    ):
        """
        An unverified user with a pending email verification token
        can still request a password reset (no conflict between the
        two token systems).
        """
        # Create a pending email verification token for this user
        _create_verification_token(unverified_user)

        # Request password reset — should work fine
        r = self._request_reset(api_client, unverified_user.email)
        assert r.status_code == status.HTTP_200_OK

        # Email verification token should still be valid (not affected)
        assert EmailVerificationToken.objects.filter(
            user=unverified_user, used=False
        ).count() == 1
