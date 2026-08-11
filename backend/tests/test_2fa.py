"""
Test Suite — 2FA (Two-Factor Authentication) Endpoints

Covers setup, verification, disable, and the complete login-with-2FA flow.
Uses pyotp directly to generate valid TOTP codes for testing.
"""

from datetime import timedelta

import pyotp
import pytest
from axes.utils import reset
from django.test.utils import override_settings
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from tests.factories import SchoolFactory, UserFactory
from tests.url_helpers import (
    AUTH_DISABLE_2FA,
    AUTH_LOGIN,
    AUTH_LOGOUT,
    AUTH_ME,
    AUTH_REGENERATE_BACKUP_CODES,
    AUTH_SETUP_2FA,
    AUTH_VERIFY_2FA,
    AUTH_VERIFY_2FA_LOGIN,
)

# ─── Fixtures ─────────────────────────────────────────────────────────────────


def _patch_throttle_rates(rates_dict):
    """
    Temporarily replace the effective throttle rates.

    DRF binds ``SimpleRateThrottle.THROTTLE_RATES`` to the api_settings dict at
    class-definition time, so ``override_settings(REST_FRAMEWORK=...)`` (which
    only swaps api_settings) never reaches it — the class attribute itself must
    be patched.
    """
    from unittest.mock import patch

    from rest_framework.throttling import SimpleRateThrottle

    return patch.object(SimpleRateThrottle, "THROTTLE_RATES", rates_dict)


@pytest.fixture
def lifted_2fa_throttles(monkeypatch):
    """
    Lift the per-IP verify-2fa-login (5/min) and login (10/min) throttle rates
    for the lifecycle tests, which fire many requests from one IP within a
    minute. The dedicated throttle tests (TestVerify2FALoginThrottle,
    TestAuthLoginThrottle) and combined_flow's phases 3–5 keep the real rates.
    """
    from rest_framework.throttling import SimpleRateThrottle

    rates = dict(SimpleRateThrottle.THROTTLE_RATES)
    rates.update(auth_verify_2fa_login="10000/minute", auth_login="10000/minute")
    monkeypatch.setattr(SimpleRateThrottle, "THROTTLE_RATES", rates)
    yield


@pytest.fixture
def school(db):
    return SchoolFactory()


@pytest.fixture
def user(db, school):
    """A regular user (student role) without 2FA enabled."""
    return UserFactory(school=school, email="test@school.edu", role="student")


@pytest.fixture
def user_with_secret(db, user):
    """User who has completed setup-2fa but hasn't verified yet."""
    secret = pyotp.random_base32()
    user.two_factor_secret = secret
    user.two_factor_enabled = False
    user.save(update_fields=["two_factor_secret", "two_factor_enabled"])
    return user, secret


@pytest.fixture
def user_with_2fa(db, user):
    """User with fully enabled 2FA."""
    secret = pyotp.random_base32()
    user.two_factor_secret = secret
    user.two_factor_enabled = True
    user.save(update_fields=["two_factor_secret", "two_factor_enabled"])
    return user, secret


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_client(db, user):
    c = APIClient()
    c.force_authenticate(user=user)
    return c


# ─── Setup2FA Tests ──────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestSetup2FA:

    def test_setup_returns_secret_and_uri(self, auth_client):
        """Authenticated user can generate a TOTP secret."""
        r = auth_client.post(AUTH_SETUP_2FA)
        assert r.status_code == status.HTTP_200_OK
        assert "secret" in r.data
        assert "provisioning_uri" in r.data
        assert len(r.data["secret"]) > 0
        # URI should contain the user's email (URL-encoded as %40)
        assert "test%40school.edu" in r.data["provisioning_uri"]

    def test_setup_saves_secret_on_user(self, auth_client, user):
        """Secret is persisted on the User model (enabled=False)."""
        r = auth_client.post(AUTH_SETUP_2FA)
        user.refresh_from_db()
        assert user.two_factor_secret == r.data["secret"]
        assert user.two_factor_enabled is False  # Not enabled until verified

    def test_setup_requires_authentication(self, api_client):
        """Unauthenticated request returns 401."""
        r = api_client.post(AUTH_SETUP_2FA)
        assert r.status_code == status.HTTP_401_UNAUTHORIZED

    def test_setup_generates_valid_totp(self, auth_client):
        """The returned secret should produce valid TOTP codes."""
        r = auth_client.post(AUTH_SETUP_2FA)
        totp = pyotp.TOTP(r.data["secret"])
        code = totp.now()
        assert len(code) == 6
        assert code.isdigit()


# ─── Verify2FA Tests ─────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestVerify2FA:

    def test_verify_with_valid_code(self, auth_client, user_with_secret):
        """Providing a valid TOTP code enables 2FA."""
        _, secret = user_with_secret
        totp = pyotp.TOTP(secret)
        code = totp.now()
        r = auth_client.post(AUTH_VERIFY_2FA, {"code": code})
        assert r.status_code == status.HTTP_200_OK
        assert r.data["detail"] == "2FA enabled successfully."
        user_with_secret[0].refresh_from_db()
        assert user_with_secret[0].two_factor_enabled is True

    def test_verify_with_invalid_code(self, auth_client, user_with_secret):
        """Invalid TOTP code returns 400."""
        r = auth_client.post(AUTH_VERIFY_2FA, {"code": "000000"})
        assert r.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid" in r.data["detail"]

    def test_verify_without_setup(self, auth_client):
        """User without a secret cannot verify 2FA."""
        r = auth_client.post(AUTH_VERIFY_2FA, {"code": "123456"})
        assert r.status_code == status.HTTP_400_BAD_REQUEST
        assert "not set up" in r.data["detail"].lower()

    def test_verify_requires_authentication(self, api_client):
        """Unauthenticated request returns 401."""
        r = api_client.post(AUTH_VERIFY_2FA, {"code": "123456"})
        assert r.status_code == status.HTTP_401_UNAUTHORIZED

    def test_verify_with_code_from_adjacent_window(self, auth_client, user_with_secret):
        """TOTP codes from ±1 time window should still work (valid_window=1)."""
        _, secret = user_with_secret
        # Generate a code from the previous time window
        import time

        past_timestamp = int(time.time()) - 30  # 30 seconds ago = previous window
        totp = pyotp.TOTP(secret)
        past_code = totp.at(past_timestamp)
        r = auth_client.post(AUTH_VERIFY_2FA, {"code": past_code})
        assert r.status_code == status.HTTP_200_OK

    def test_verify_with_expired_code_rejected(self, auth_client, user_with_secret):
        """TOTP codes from 2+ windows away should be rejected."""
        _, secret = user_with_secret
        totp = pyotp.TOTP(secret)
        import time

        old_timestamp = int(time.time()) - 90  # 90 seconds ago = 3 windows back
        old_code = totp.at(old_timestamp)
        r = auth_client.post(AUTH_VERIFY_2FA, {"code": old_code})
        assert r.status_code == status.HTTP_400_BAD_REQUEST


# ─── Disable2FA Tests ────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestDisable2FA:

    def test_disable_with_correct_password(self, auth_client, user_with_2fa):
        """User can disable 2FA with correct password."""
        user, _ = user_with_2fa
        r = auth_client.post(AUTH_DISABLE_2FA, {"password": "TestPass@1234"})
        assert r.status_code == status.HTTP_200_OK
        assert r.data["detail"] == "2FA disabled."
        user.refresh_from_db()
        assert user.two_factor_enabled is False
        assert user.two_factor_secret == ""

    def test_disable_with_wrong_password(self, auth_client, user_with_2fa):
        """Wrong password returns 400."""
        r = auth_client.post(AUTH_DISABLE_2FA, {"password": "WrongPass@9999"})
        assert r.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid password" in r.data["detail"]

    def test_disable_requires_authentication(self, api_client):
        """Unauthenticated request returns 401."""
        r = api_client.post(AUTH_DISABLE_2FA, {"password": "Test"})
        assert r.status_code == status.HTTP_401_UNAUTHORIZED

    def test_disable_clears_secret(self, auth_client, user_with_2fa):
        """Secret is also cleared on disable."""
        auth_client.post(AUTH_DISABLE_2FA, {"password": "TestPass@1234"})
        user_with_2fa[0].refresh_from_db()
        assert user_with_2fa[0].two_factor_secret == ""


# ─── Backup Codes Tests ───────────────────────────────────────────────────────


@pytest.mark.django_db
class TestBackupCodes:

    def test_setup_returns_backup_codes(self, auth_client):
        """Setup2FA returns 8 backup codes in the response."""
        r = auth_client.post(AUTH_SETUP_2FA)
        assert r.status_code == status.HTTP_200_OK
        assert "backup_codes" in r.data
        assert len(r.data["backup_codes"]) == 8
        # Each code should match XXXXX-XXXXX format
        import re

        for code in r.data["backup_codes"]:
            assert re.match(r"^[A-Z0-9]{5}-[A-Z0-9]{5}$", code), f"Invalid format: {code}"

    def test_backup_codes_stored_hashed(self, auth_client, user):
        """Backup codes are stored as SHA-256 hashes in the DB."""
        from services.auth.models import TwoFactorBackupCode

        r = auth_client.post(AUTH_SETUP_2FA)
        codes_in_db = TwoFactorBackupCode.objects.filter(user=user)
        assert codes_in_db.count() == 8

        # Verify each plain-text code's SHA-256 hash exists in the DB
        import hashlib

        for code in r.data["backup_codes"]:
            hashed = hashlib.sha256(code.encode()).hexdigest()
            assert TwoFactorBackupCode.objects.filter(user=user, hashed_code=hashed).exists()

    def test_backup_code_can_be_used_to_login(self, api_client, user_with_2fa):
        """A valid backup code can log the user in via verify-2fa-login."""
        from services.auth.models import TwoFactorBackupCode

        user, secret = user_with_2fa

        # Create a valid backup code directly in the DB
        import hashlib

        plain_code = "ABCDE-12345"
        hashed = hashlib.sha256(plain_code.encode()).hexdigest()
        TwoFactorBackupCode.objects.create(user=user, hashed_code=hashed, used=False)

        r = api_client.post(
            AUTH_VERIFY_2FA_LOGIN,
            {
                "user_id": str(user.id),
                "code": plain_code,
            },
        )
        assert r.status_code == status.HTTP_200_OK
        assert "access" in r.data

    def test_backup_code_marked_used_after_login(self, api_client, user_with_2fa):
        """Backup code is marked as used after a successful login."""
        from services.auth.models import TwoFactorBackupCode

        user, secret = user_with_2fa

        import hashlib

        plain_code = "FGHIJ-67890"
        hashed = hashlib.sha256(plain_code.encode()).hexdigest()
        bc = TwoFactorBackupCode.objects.create(user=user, hashed_code=hashed, used=False)

        api_client.post(
            AUTH_VERIFY_2FA_LOGIN,
            {
                "user_id": str(user.id),
                "code": plain_code,
            },
        )

        bc.refresh_from_db()
        assert bc.used is True

    def test_backup_code_cannot_be_reused(self, api_client, user_with_2fa):
        """Once used, a backup code cannot be used again."""
        from services.auth.models import TwoFactorBackupCode

        user, secret = user_with_2fa

        import hashlib

        plain_code = "KLMNO-24680"
        hashed = hashlib.sha256(plain_code.encode()).hexdigest()
        TwoFactorBackupCode.objects.create(user=user, hashed_code=hashed, used=False)

        # First use — should succeed
        r1 = api_client.post(
            AUTH_VERIFY_2FA_LOGIN,
            {
                "user_id": str(user.id),
                "code": plain_code,
            },
        )
        assert r1.status_code == status.HTTP_200_OK

        # Second use — should fail
        r2 = api_client.post(
            AUTH_VERIFY_2FA_LOGIN,
            {
                "user_id": str(user.id),
                "code": plain_code,
            },
        )
        assert r2.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid" in r2.data["detail"]

    def test_invalid_backup_code_rejected(self, api_client, user_with_2fa):
        """An unknown backup code returns 400."""
        user, secret = user_with_2fa

        r = api_client.post(
            AUTH_VERIFY_2FA_LOGIN,
            {
                "user_id": str(user.id),
                "code": "NONEX-ISTEN",
            },
        )
        assert r.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid" in r.data["detail"]

    def test_backup_codes_cleaned_on_disable(self, auth_client, user_with_2fa):
        """Disabling 2FA removes all backup codes from the DB."""
        from services.auth.models import TwoFactorBackupCode

        user, secret = user_with_2fa

        # Create some backup codes
        import hashlib

        for code in ["FIRST-11111", "SECON-22222", "THIRD-33333"]:
            hashed = hashlib.sha256(code.encode()).hexdigest()
            TwoFactorBackupCode.objects.create(user=user, hashed_code=hashed, used=False)

        assert TwoFactorBackupCode.objects.filter(user=user).count() == 3

        r = auth_client.post(AUTH_DISABLE_2FA, {"password": "TestPass@1234"})
        assert r.status_code == status.HTTP_200_OK

        # All backup codes should be deleted
        assert TwoFactorBackupCode.objects.filter(user=user).count() == 0

    def test_regenerate_backup_codes(self, auth_client, user_with_2fa):
        """Regenerate endpoint creates new codes and invalidates old ones."""
        from services.auth.models import TwoFactorBackupCode

        user, secret = user_with_2fa

        # Create some old backup codes
        import hashlib

        for code in ["OLDCD-11111", "OLDCD-22222"]:
            hashed = hashlib.sha256(code.encode()).hexdigest()
            TwoFactorBackupCode.objects.create(user=user, hashed_code=hashed, used=False)

        r = auth_client.post(
            AUTH_REGENERATE_BACKUP_CODES,
            {
                "password": "TestPass@1234",
            },
        )
        assert r.status_code == status.HTTP_200_OK
        assert "backup_codes" in r.data
        assert len(r.data["backup_codes"]) == 8

        # Old codes should be deleted
        assert TwoFactorBackupCode.objects.filter(user=user).count() == 8
        # Old codes shouldn't exist anymore
        old_hashed = hashlib.sha256("OLDCD-11111".encode()).hexdigest()
        assert not TwoFactorBackupCode.objects.filter(user=user, hashed_code=old_hashed).exists()

    def test_regenerate_requires_password(self, auth_client, user_with_2fa):
        """Regenerate without password (or wrong password) returns 400."""
        r = auth_client.post(AUTH_REGENERATE_BACKUP_CODES, {"password": "WrongPass@9999"})
        assert r.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid password" in r.data["detail"]

    def test_regenerate_requires_2fa_enabled(self, auth_client, user):
        """User without 2FA cannot regenerate backup codes."""
        r = auth_client.post(
            AUTH_REGENERATE_BACKUP_CODES,
            {
                "password": "TestPass@1234",
            },
        )
        assert r.status_code == status.HTTP_400_BAD_REQUEST
        assert "not enabled" in r.data["detail"].lower()

    def test_full_flow_with_backup_codes(self, api_client, user):
        """
        End-to-end: setup → get backup codes → login fails (requires 2FA) →
        login with backup code → access API.
        """
        # Step 1: Login and get token
        login = api_client.post(
            AUTH_LOGIN,
            {
                "email": user.email,
                "password": "TestPass@1234",
            },
        )
        assert "access" in login.data
        token = login.data["access"]

        # Step 2: Setup 2FA (get backup codes)
        setup_client = APIClient()
        setup_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        setup_r = setup_client.post(AUTH_SETUP_2FA)
        assert setup_r.status_code == status.HTTP_200_OK
        backup_codes = setup_r.data["backup_codes"]
        assert len(backup_codes) == 8
        secret = setup_r.data["secret"]

        # Step 3: Enable 2FA with TOTP
        import pyotp

        totp = pyotp.TOTP(secret)
        verify_r = setup_client.post(AUTH_VERIFY_2FA, {"code": totp.now()})
        assert verify_r.status_code == status.HTTP_200_OK

        # Step 4: Logout and login — should require 2FA
        api_client.post(AUTH_LOGOUT, {"refresh": login.data["refresh"]})
        login2 = api_client.post(
            AUTH_LOGIN,
            {
                "email": user.email,
                "password": "TestPass@1234",
            },
        )
        assert login2.data.get("requires_2fa") is True
        user_id = login2.data["user_id"]

        # Step 5: Use a backup code instead of TOTP
        backup_code = backup_codes[0]
        final = api_client.post(
            AUTH_VERIFY_2FA_LOGIN,
            {
                "user_id": user_id,
                "code": backup_code,
            },
        )
        assert final.status_code == status.HTTP_200_OK
        assert "access" in final.data
        assert final.data["user"]["email"] == user.email

        # Step 6: The backup code cannot be reused
        r3 = api_client.post(
            AUTH_VERIFY_2FA_LOGIN,
            {
                "user_id": user_id,
                "code": backup_code,
            },
        )
        assert r3.status_code == status.HTTP_400_BAD_REQUEST

        # Step 7: Use another backup code
        backup_code2 = backup_codes[1]
        final2 = api_client.post(
            AUTH_VERIFY_2FA_LOGIN,
            {
                "user_id": user_id,
                "code": backup_code2,
            },
        )
        assert final2.status_code == status.HTTP_200_OK
        assert "access" in final2.data


# ─── Backup Code Lockout Tests ────────────────────────────────────────────────


# These lifecycle tests fire many sequential verify-2fa-login + login requests
# from one IP within a single minute — far beyond the real per-IP throttles
# (5/min verify, 10/min login). The dedicated throttle classes below test the
# throttles at their real rates; here they are lifted so lockout semantics are
# what is exercised.
@pytest.mark.django_db
@pytest.mark.slow
class TestBackupCodeLockout:

    def test_invalid_backup_code_increments_attempts(self, api_client, user_with_2fa):
        """A failed backup code attempt increments the counter."""
        user, _ = user_with_2fa

        for i in range(1, 4):
            r = api_client.post(
                AUTH_VERIFY_2FA_LOGIN,
                {
                    "user_id": str(user.id),
                    "code": f"WRONG-{i:05d}",
                },
            )
            # First 2 attempts return 400 with remaining count;
            # the 3rd triggers the lockout and returns 429
            if i < 3:
                assert r.status_code == status.HTTP_400_BAD_REQUEST
                assert "remaining" in r.data["detail"].lower()
            else:
                assert r.status_code == status.HTTP_429_TOO_MANY_REQUESTS
                assert "try again in" in r.data["detail"].lower()

        user.refresh_from_db()
        assert user.backup_code_failed_attempts == 3
        assert user.backup_code_locked_until is not None

    def test_lockout_after_three_failed_attempts(self, api_client, user_with_2fa):
        """After 3 failed backup code attempts, user is locked out."""
        user, _ = user_with_2fa

        # 3 failed attempts
        for i in range(3):
            api_client.post(
                AUTH_VERIFY_2FA_LOGIN,
                {
                    "user_id": str(user.id),
                    "code": f"WRONG-{i:05d}",
                },
            )

        # 4th attempt should be locked out
        r = api_client.post(
            AUTH_VERIFY_2FA_LOGIN,
            {
                "user_id": str(user.id),
                "code": "WRONG-XXXXX",
            },
        )
        assert r.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert "try again in" in r.data["detail"].lower()

    def test_totp_still_works_during_backup_code_lockout(self, api_client, user_with_2fa):
        """TOTP verification still works even when backup code lockout is active."""
        user, secret = user_with_2fa

        # Trigger backup code lockout
        for i in range(3):
            api_client.post(
                AUTH_VERIFY_2FA_LOGIN,
                {
                    "user_id": str(user.id),
                    "code": f"WRONG-{i:05d}",
                },
            )

        # TOTP should still work
        totp = pyotp.TOTP(secret)
        r = api_client.post(
            AUTH_VERIFY_2FA_LOGIN,
            {
                "user_id": str(user.id),
                "code": totp.now(),
            },
        )
        assert r.status_code == status.HTTP_200_OK
        assert "access" in r.data

    def test_successful_backup_code_resets_lockout(self, api_client, user_with_2fa):
        """A successful backup code login resets the failed attempt counter."""
        from services.auth.models import TwoFactorBackupCode

        user, secret = user_with_2fa
        import hashlib

        plain_code = "RESET-12345"
        hashed = hashlib.sha256(plain_code.encode()).hexdigest()
        TwoFactorBackupCode.objects.create(user=user, hashed_code=hashed, used=False)

        # One failed attempt
        r = api_client.post(
            AUTH_VERIFY_2FA_LOGIN,
            {
                "user_id": str(user.id),
                "code": "WRONG-XXXXX",
            },
        )
        assert r.status_code == status.HTTP_400_BAD_REQUEST

        user.refresh_from_db()
        assert user.backup_code_failed_attempts == 1

        # Successful backup code login
        r = api_client.post(
            AUTH_VERIFY_2FA_LOGIN,
            {
                "user_id": str(user.id),
                "code": plain_code,
            },
        )
        assert r.status_code == status.HTTP_200_OK

        user.refresh_from_db()
        assert user.backup_code_failed_attempts == 0
        assert user.backup_code_locked_until is None

    def test_regenerate_backup_codes_resets_lockout(self, auth_client, user_with_2fa):
        """Regenerating backup codes resets the lockout state."""
        user, secret = user_with_2fa

        # Set some failed attempts manually
        user.backup_code_failed_attempts = 2
        user.backup_code_locked_until = timezone.now() + timedelta(minutes=30)
        user.save()

        # Regenerate codes
        r = auth_client.post(
            AUTH_REGENERATE_BACKUP_CODES,
            {
                "password": "TestPass@1234",
            },
        )
        assert r.status_code == status.HTTP_200_OK

        user.refresh_from_db()
        assert user.backup_code_failed_attempts == 0
        assert user.backup_code_locked_until is None

    def test_disable_2fa_resets_lockout(self, auth_client, user_with_2fa):
        """Disabling 2FA resets the lockout state."""
        user, secret = user_with_2fa

        # Set some failed attempts manually
        user.backup_code_failed_attempts = 3
        user.backup_code_locked_until = timezone.now() + timedelta(minutes=30)
        user.save()

        # Disable 2FA
        r = auth_client.post(AUTH_DISABLE_2FA, {"password": "TestPass@1234"})
        assert r.status_code == status.HTTP_200_OK

        user.refresh_from_db()
        assert user.backup_code_failed_attempts == 0
        assert user.backup_code_locked_until is None

    def test_lockout_message_shows_remaining_seconds(self, api_client, user_with_2fa):
        """Lockout response includes the remaining lockout time."""
        user, _ = user_with_2fa

        # Trigger lockout
        for i in range(3):
            api_client.post(
                AUTH_VERIFY_2FA_LOGIN,
                {
                    "user_id": str(user.id),
                    "code": f"WRONG-{i:05d}",
                },
            )

        r = api_client.post(
            AUTH_VERIFY_2FA_LOGIN,
            {
                "user_id": str(user.id),
                "code": "WRONG-XXXXX",
            },
        )
        assert r.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert "Try again in" in r.data["detail"]
        import re

        seconds_match = re.search(r"(\d+)", r.data["detail"])
        assert seconds_match is not None
        assert int(seconds_match.group(1)) > 0

    def test_backup_code_lockout_integration(self, api_client, user_with_2fa, lifted_2fa_throttles):
        """
        Comprehensive integration: 3 bad backup codes → locked out →
        TOTP still works → regenerate codes → lockout reset →
        backup code works again.
        """
        import hashlib

        from services.auth.models import TwoFactorBackupCode

        user, secret = user_with_2fa

        # Create a couple of valid backup codes for later use
        valid_code = "VALID-11111"
        another_valid = "VALID-22222"
        for code in [valid_code, another_valid]:
            hashed = hashlib.sha256(code.encode()).hexdigest()
            TwoFactorBackupCode.objects.create(user=user, hashed_code=hashed, used=False)

        # ── Phase 1: 3 bad backup codes → locked out ────────────────────────

        # First 2 wrong attempts → 400 with a remaining count; the 3rd reaches
        # the lockout limit and is rejected immediately with 429.
        for i in range(2):
            r = api_client.post(
                AUTH_VERIFY_2FA_LOGIN,
                {
                    "user_id": str(user.id),
                    "code": f"WRONG-{i:05d}",
                },
            )
            assert r.status_code == status.HTTP_400_BAD_REQUEST
            expected_remaining = 3 - i - 1
            if expected_remaining > 0:
                assert str(expected_remaining) in r.data["detail"].lower()

        r = api_client.post(
            AUTH_VERIFY_2FA_LOGIN,
            {
                "user_id": str(user.id),
                "code": "WRONG-00002",
            },
        )
        assert r.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert "try again in" in r.data["detail"].lower()

        # Verify lockout state in DB
        user.refresh_from_db()
        assert user.backup_code_failed_attempts == 3
        assert user.backup_code_locked_until is not None

        # 4th attempt should be locked out (429)
        r = api_client.post(
            AUTH_VERIFY_2FA_LOGIN,
            {
                "user_id": str(user.id),
                "code": "WRONG-XXXXX",
            },
        )
        assert r.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert "try again in" in r.data["detail"].lower()

        # Even a valid backup code should be rejected during lockout
        r = api_client.post(
            AUTH_VERIFY_2FA_LOGIN,
            {
                "user_id": str(user.id),
                "code": valid_code,
            },
        )
        assert r.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert "try again in" in r.data["detail"].lower()

        # ── Phase 2: TOTP still works during lockout ────────────────────────

        totp = pyotp.TOTP(secret)
        r = api_client.post(
            AUTH_VERIFY_2FA_LOGIN,
            {
                "user_id": str(user.id),
                "code": totp.now(),
            },
        )
        assert r.status_code == status.HTTP_200_OK
        assert "access" in r.data

        # ── Phase 3: Login again (needs 2FA again) and regenerate codes ───────

        # Login to get a fresh user_id
        login = api_client.post(
            AUTH_LOGIN,
            {
                "email": user.email,
                "password": "TestPass@1234",
            },
        )
        assert login.data.get("requires_2fa") is True
        user_id = login.data["user_id"]

        # TOTP to get a token to authenticate the regenerate request
        totp2 = pyotp.TOTP(secret)
        totp_r = api_client.post(
            AUTH_VERIFY_2FA_LOGIN,
            {
                "user_id": user_id,
                "code": totp2.now(),
            },
        )
        assert totp_r.status_code == status.HTTP_200_OK
        token = totp_r.data["access"]

        # Regenerate backup codes (requires auth + password)
        auth_api = APIClient()
        auth_api.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        user.refresh_from_db()
        assert user.backup_code_failed_attempts == 3  # Still locked out
        assert user.backup_code_locked_until is not None

        r = auth_api.post(
            AUTH_REGENERATE_BACKUP_CODES,
            {
                "password": "TestPass@1234",
            },
        )
        assert r.status_code == status.HTTP_200_OK
        assert "backup_codes" in r.data
        new_codes = r.data["backup_codes"]
        assert len(new_codes) == 8

        # ── Phase 4: Lockout reset — backup codes work again ─────────────────

        user.refresh_from_db()
        assert user.backup_code_failed_attempts == 0
        assert user.backup_code_locked_until is None

        # Login again and use a new backup code
        login2 = api_client.post(
            AUTH_LOGIN,
            {
                "email": user.email,
                "password": "TestPass@1234",
            },
        )
        user_id2 = login2.data["user_id"]

        r = api_client.post(
            AUTH_VERIFY_2FA_LOGIN,
            {
                "user_id": user_id2,
                "code": new_codes[0],
            },
        )
        assert r.status_code == status.HTTP_200_OK
        assert "access" in r.data

        # Old codes should no longer work (invalidated by regenerate)
        user.refresh_from_db()
        old_hashed = hashlib.sha256(valid_code.encode()).hexdigest()
        assert not TwoFactorBackupCode.objects.filter(user=user, hashed_code=old_hashed, used=False).exists()

    def test_lockout_auto_expires_after_30_minutes(self, api_client, user_with_2fa):
        """
        Backup code lockout automatically expires after 30 minutes.
        Uses mocked timezone.now() to simulate the passage of time.
        """
        from unittest.mock import patch

        user, _ = user_with_2fa

        # Step 1: Trigger lockout with 3 failed attempts
        for i in range(3):
            api_client.post(
                AUTH_VERIFY_2FA_LOGIN,
                {
                    "user_id": str(user.id),
                    "code": f"WRONG-{i:05d}",
                },
            )

        user.refresh_from_db()
        assert user.backup_code_failed_attempts == 3
        assert user.backup_code_locked_until is not None

        # Step 2: Verify lockout is active
        r = api_client.post(
            AUTH_VERIFY_2FA_LOGIN,
            {
                "user_id": str(user.id),
                "code": "WRONG-XXXXX",
            },
        )
        assert r.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert "try again in" in r.data["detail"].lower()

        # Step 3: Advance time by 31 minutes (past the 30-minute lockout)
        future_time = timezone.now() + timedelta(minutes=31)
        with patch("django.utils.timezone.now", return_value=future_time):
            user.refresh_from_db()
            # The lockout_until is still set in the past relative to our mocked now
            # But the endpoint calls _check_backup_code_lockout which reads
            # user.backup_code_locked_until from the DB and compares with timezone.now()
            # The user object was loaded before the patch, so we need a fresh API call
            # that re-loads the user from DB
            r = api_client.post(
                AUTH_VERIFY_2FA_LOGIN,
                {
                    "user_id": str(user.id),
                    "code": "WRONG-XXXXX",
                },
            )

        # Step 4: The old lockout DID expire (_check_backup_code_lockout returned
        # not-locked since time > locked_until). However, the failed attempt
        # increments the counter to 4 (still >= 3), which triggers a NEW lockout.
        # So we get 429 with the "locked out" message, not 400.
        assert r.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert "locked out" in r.data["detail"].lower()

        # Step 5: Lockout expired — counter remained, so the next failed attempt
        # (within the patched block) incremented it to 4 and triggered a new lockout.
        user.refresh_from_db()
        assert user.backup_code_failed_attempts == 4
        assert user.backup_code_locked_until is not None
        assert user.backup_code_locked_until > timezone.now()


# ─── Backup Codes Remaining (me endpoint) Tests ────────────────────────────────


@pytest.mark.django_db
class TestBackupCodesRemaining:
    """
    Tests for the backup_codes_remaining field exposed via /auth/me/.
    The UserProfileSerializer returns None when 2FA is disabled, or the
    count of unused backup codes when 2FA is enabled.
    """

    def test_returns_none_when_2fa_disabled(self, auth_client):
        """User without 2FA gets null backup_codes_remaining."""
        r = auth_client.get(AUTH_ME)
        assert r.status_code == status.HTTP_200_OK
        assert r.data["backup_codes_remaining"] is None

    def test_returns_correct_count_after_setup(self, auth_client, user):
        """After 2FA setup and enable, backup_codes_remaining shows 8."""
        # Setup 2FA
        setup_r = auth_client.post(AUTH_SETUP_2FA)
        assert setup_r.status_code == status.HTTP_200_OK

        # Enable 2FA with TOTP
        import pyotp

        secret = setup_r.data["secret"]
        totp = pyotp.TOTP(secret)
        verify_r = auth_client.post(AUTH_VERIFY_2FA, {"code": totp.now()})
        assert verify_r.status_code == status.HTTP_200_OK

        # Check me endpoint
        r = auth_client.get(AUTH_ME)
        assert r.status_code == status.HTTP_200_OK
        assert r.data["backup_codes_remaining"] == 8
        assert r.data["two_factor_enabled"] is True

    def test_decrements_after_backup_code_use(self, api_client, user):
        """Using a backup code to login decreases backup_codes_remaining."""
        # Full setup flow: login → setup 2FA → enable → login with backup code → check me
        login = api_client.post(
            AUTH_LOGIN,
            {
                "email": user.email,
                "password": "TestPass@1234",
            },
        )
        token = login.data["access"]

        auth = APIClient()
        auth.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        # Setup + enable 2FA
        setup_r = auth.post(AUTH_SETUP_2FA)
        backup_codes = setup_r.data["backup_codes"]
        import pyotp

        totp = pyotp.TOTP(setup_r.data["secret"])
        auth.post(AUTH_VERIFY_2FA, {"code": totp.now()})

        # Check initial count via me
        r = auth.get(AUTH_ME)
        assert r.data["backup_codes_remaining"] == 8

        # Logout
        api_client.post(AUTH_LOGOUT, {"refresh": login.data["refresh"]})

        # Login again — requires 2FA
        login2 = api_client.post(
            AUTH_LOGIN,
            {
                "email": user.email,
                "password": "TestPass@1234",
            },
        )
        user_id = login2.data["user_id"]

        # Use a backup code to login
        backup_code = backup_codes[0]
        final = api_client.post(
            AUTH_VERIFY_2FA_LOGIN,
            {
                "user_id": user_id,
                "code": backup_code,
            },
        )
        assert final.status_code == status.HTTP_200_OK
        new_token = final.data["access"]

        # Check me endpoint with new token — count should be 7
        auth2 = APIClient()
        auth2.credentials(HTTP_AUTHORIZATION=f"Bearer {new_token}")
        r = auth2.get(AUTH_ME)
        assert r.status_code == status.HTTP_200_OK
        assert r.data["backup_codes_remaining"] == 7

    def test_resets_to_8_after_regenerate(self, auth_client, user_with_2fa):
        """Regenerating backup codes resets backup_codes_remaining to 8."""
        import hashlib

        from services.auth.models import TwoFactorBackupCode

        user, _ = user_with_2fa

        # Use up some codes manually
        for code in ["USED-11111", "USED-22222"]:
            hashed = hashlib.sha256(code.encode()).hexdigest()
            TwoFactorBackupCode.objects.create(user=user, hashed_code=hashed, used=True)

        # Create 3 unused codes
        for code in ["LEFT-33333", "LEFT-44444", "LEFT-55555"]:
            hashed = hashlib.sha256(code.encode()).hexdigest()
            TwoFactorBackupCode.objects.create(user=user, hashed_code=hashed, used=False)

        # Check count via me
        r = auth_client.get(AUTH_ME)
        assert r.data["backup_codes_remaining"] == 3

        # Regenerate
        auth_client.post(AUTH_REGENERATE_BACKUP_CODES, {"password": "TestPass@1234"})

        # Check count reset to 8
        r = auth_client.get(AUTH_ME)
        assert r.data["backup_codes_remaining"] == 8

    def test_returns_none_after_2fa_disabled(self, auth_client, user_with_2fa):
        """Disabling 2FA makes backup_codes_remaining return None."""
        # First verify it shows a count
        r = auth_client.get(AUTH_ME)
        assert r.data["backup_codes_remaining"] is not None
        assert isinstance(r.data["backup_codes_remaining"], int)

        # Disable 2FA
        auth_client.post(AUTH_DISABLE_2FA, {"password": "TestPass@1234"})

        # Now it should be None
        r = auth_client.get(AUTH_ME)
        assert r.data["backup_codes_remaining"] is None
        assert r.data["two_factor_enabled"] is False

    def test_requires_authentication(self, api_client):
        """Unauthenticated request to me returns 401."""
        r = api_client.get(AUTH_ME)
        assert r.status_code == status.HTTP_401_UNAUTHORIZED


# ─── Login with 2FA Flow Tests ───────────────────────────────────────────────


@pytest.mark.django_db
class TestLoginWith2FA:

    def test_login_returns_requires_2fa_when_enabled(self, api_client, user_with_2fa):
        """Login with 2FA returns requires_2fa: True instead of tokens."""
        user, _ = user_with_2fa
        r = api_client.post(
            AUTH_LOGIN,
            {
                "email": user.email,
                "password": "TestPass@1234",
            },
        )
        assert r.status_code == status.HTTP_200_OK
        assert r.data.get("requires_2fa") is True
        assert "user_id" in r.data
        assert "access" not in r.data  # No JWT yet
        assert "refresh" not in r.data

    def test_login_returns_requires_2fa_false_when_disabled(self, api_client, user):
        """Login without 2FA returns tokens normally."""
        r = api_client.post(
            AUTH_LOGIN,
            {
                "email": user.email,
                "password": "TestPass@1234",
            },
        )
        assert r.status_code == status.HTTP_200_OK
        assert r.data.get("requires_2fa") is not True
        assert "access" in r.data
        assert "refresh" in r.data

    def test_verify_2fa_login_completes_authentication(self, api_client, user_with_2fa):
        """After login with requires_2fa, verify-2fa-login returns JWT."""
        user, secret = user_with_2fa
        totp = pyotp.TOTP(secret)
        code = totp.now()
        r = api_client.post(
            AUTH_VERIFY_2FA_LOGIN,
            {
                "user_id": str(user.id),
                "code": code,
            },
        )
        assert r.status_code == status.HTTP_200_OK
        assert "access" in r.data
        assert "refresh" in r.data
        assert r.data["user"]["email"] == user.email

    def test_verify_2fa_login_invalid_code(self, api_client, user_with_2fa):
        """Invalid TOTP code during login returns 400."""
        user, _ = user_with_2fa
        r = api_client.post(
            AUTH_VERIFY_2FA_LOGIN,
            {
                "user_id": str(user.id),
                "code": "000000",
            },
        )
        assert r.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid" in r.data["detail"]

    def test_verify_2fa_login_unknown_user(self, api_client):
        """Unknown user_id returns 400."""
        r = api_client.post(
            AUTH_VERIFY_2FA_LOGIN,
            {
                "user_id": "00000000-0000-0000-0000-000000000000",
                "code": "123456",
            },
        )
        assert r.status_code == status.HTTP_400_BAD_REQUEST

    def test_verify_2fa_login_user_without_2fa(self, api_client, user):
        """User without 2FA enabled cannot use verify-2fa-login."""
        r = api_client.post(
            AUTH_VERIFY_2FA_LOGIN,
            {
                "user_id": str(user.id),
                "code": "123456",
            },
        )
        assert r.status_code == status.HTTP_400_BAD_REQUEST
        assert "not enabled" in r.data["detail"]

    def test_verify_2fa_login_with_expired_code(self, api_client, user_with_2fa):
        """TOTP code from 3+ windows away is rejected during login."""
        user, secret = user_with_2fa
        totp = pyotp.TOTP(secret)
        import time

        old_code = totp.at(int(time.time()) - 90)
        r = api_client.post(
            AUTH_VERIFY_2FA_LOGIN,
            {
                "user_id": str(user.id),
                "code": old_code,
            },
        )
        assert r.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid" in r.data["detail"]

    def test_full_2fa_login_flow(self, api_client, user):
        """End-to-end: setup → enable → login-with-2fa → verify-login → access API."""

        # Step 1: Login without 2FA (normal JWT flow)
        # We need to be authenticated to set up 2FA, so login first
        login = api_client.post(
            AUTH_LOGIN,
            {
                "email": user.email,
                "password": "TestPass@1234",
            },
        )
        assert "access" in login.data
        token = login.data["access"]

        # Step 2: Setup 2FA
        setup_client = APIClient()
        setup_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        setup_r = setup_client.post(AUTH_SETUP_2FA)
        assert setup_r.status_code == status.HTTP_200_OK
        secret = setup_r.data["secret"]

        # Step 3: Verify 2FA with a valid TOTP code
        totp = pyotp.TOTP(secret)
        code = totp.now()
        verify_r = setup_client.post(AUTH_VERIFY_2FA, {"code": code})
        assert verify_r.status_code == status.HTTP_200_OK

        # Step 4: Logout and login again — should now require 2FA
        api_client.post(AUTH_LOGOUT, {"refresh": login.data["refresh"]})
        login2 = api_client.post(
            AUTH_LOGIN,
            {
                "email": user.email,
                "password": "TestPass@1234",
            },
        )
        assert login2.data.get("requires_2fa") is True
        user_id = login2.data["user_id"]

        # Step 5: Complete login with TOTP code
        code2 = pyotp.TOTP(secret).now()
        final = api_client.post(
            AUTH_VERIFY_2FA_LOGIN,
            {
                "user_id": user_id,
                "code": code2,
            },
        )
        assert final.status_code == status.HTTP_200_OK
        assert "access" in final.data
        assert final.data["user"]["email"] == user.email

        # Step 6: Use the final token to access a protected endpoint
        protected_client = APIClient()
        protected_client.credentials(HTTP_AUTHORIZATION=f"Bearer {final.data['access']}")
        me_r = protected_client.get("/api/v1/auth/me/")
        assert me_r.status_code == status.HTTP_200_OK
        assert me_r.data["two_factor_enabled"] is True

        # Step 7: Disable 2FA
        disable_client = APIClient()
        disable_client.credentials(HTTP_AUTHORIZATION=f"Bearer {final.data['access']}")
        disable_r = disable_client.post(AUTH_DISABLE_2FA, {"password": "TestPass@1234"})
        assert disable_r.status_code == status.HTTP_200_OK

        # Step 8: Login again — should work without 2FA
        login3 = api_client.post(
            AUTH_LOGIN,
            {
                "email": user.email,
                "password": "TestPass@1234",
            },
        )
        assert "access" in login3.data
        assert login3.data.get("requires_2fa") is not True


# ─── Full Zero-Mock Integration Test ──────────────────────────────────────────


@pytest.mark.django_db
@pytest.mark.slow
class TestBackupCodeLockoutZeroMock:
    """
    Comprehensive, zero-mock integration test that exercises the entire
    backup code lifecycle through the real HTTP layer.

    Unlike test_backup_code_lockout_integration, this test never creates
    backup codes directly in the database. Every backup code is obtained
    from the setup-2fa HTTP response, and every state change is triggered
    via real API calls. The only DB access is for final state assertions
    (refresh_from_db, queryset counts).
    """

    def _login_and_get_token(self, api_client, user):
        """Helper: login and return the full response data."""
        r = api_client.post(
            AUTH_LOGIN,
            {
                "email": user.email,
                "password": "TestPass@1234",
            },
        )
        assert r.status_code == status.HTTP_200_OK
        return r.data

    def _setup_2fa_via_http(self, token):
        """Helper: setup 2FA with a bearer token, returns (secret, backup_codes)."""
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        r = client.post(AUTH_SETUP_2FA)
        assert r.status_code == status.HTTP_200_OK
        return r.data["secret"], r.data["backup_codes"]

    def _enable_2fa_via_http(self, token, secret):
        """Helper: verify TOTP to enable 2FA."""
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        totp = pyotp.TOTP(secret)
        r = client.post(AUTH_VERIFY_2FA, {"code": totp.now()})
        assert r.status_code == status.HTTP_200_OK
        return r.data

    def _complete_2fa_login(self, api_client, login_data, code):
        """Helper: complete the 2FA login step with a code (TOTP or backup)."""
        r = api_client.post(
            AUTH_VERIFY_2FA_LOGIN,
            {
                "user_id": login_data["user_id"],
                "code": code,
            },
        )
        return r

    def _get_me(self, token):
        """Helper: fetch /auth/me/ with a bearer token."""
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        return client.get(AUTH_ME)

    def test_full_http_lifecycle(self, api_client, user, lifted_2fa_throttles):
        """
        Complete lifecycle tested entirely through HTTP:

        Phase 1 — Setup:
          1. Login → get JWT
          2. Setup 2FA → get backup_codes + secret from HTTP response
          3. Enable 2FA with TOTP
          4. Login → receives requires_2fa with backup_codes_remaining: 8
          5. Complete login with TOTP → get final token
          6. Check /auth/me/ → backup_codes_remaining == 8

        Phase 2 — Use backup codes (2 successful uses):
          7. Login again → use backup code #1 → success
          8. Login again → check /auth/me/ → backup_codes_remaining == 7
          9. Login again → use backup code #2 → success
         10. Login again → check /auth/me/ → backup_codes_remaining == 6

        Phase 3 — Lockout:
         11. Login again → 3 failed backup code attempts
         12. 4th attempt → 429 (locked out)
         13. A valid backup code (#3) also rejected → 429
         14. TOTP still works during lockout → 200

        Phase 4 — Regenerate + verify reset:
         15. Login + TOTP → get token
         16. Regenerate codes via HTTP
         17. Check /auth/me/ → backup_codes_remaining == 8
         18. Login again → use new backup code #1 → success
         19. Old code #1 is now invalid → 400
        """
        import hashlib

        from services.auth.models import TwoFactorBackupCode

        # ════════════════════════════════════════════════════════════════
        # PHASE 1 ── Setup
        # ════════════════════════════════════════════════════════════════
        # 1. Login to get a token
        login1 = self._login_and_get_token(api_client, user)
        token1 = login1["access"]

        # 2. Setup 2FA → get backup codes from the HTTP response
        secret, backup_codes = self._setup_2fa_via_http(token1)
        assert len(backup_codes) == 8, f"Expected 8 backup codes, got {len(backup_codes)}"

        # 3. Enable 2FA with TOTP
        self._enable_2fa_via_http(token1, secret)

        # Verify 2FA is enabled in the DB
        user.refresh_from_db()
        assert user.two_factor_enabled is True

        # 4. Login again → should return requires_2fa with backup_codes_remaining
        login2 = self._login_and_get_token(api_client, user)
        assert login2.get("requires_2fa") is True
        assert login2.get("user_id") == str(user.id)
        assert "access" not in login2, "JWT should not be returned before 2FA"

        # ★ Verify backup_codes_remaining in the login response
        assert "backup_codes_remaining" in login2, "Login response should include backup_codes_remaining"
        assert login2["backup_codes_remaining"] == 8, f"Expected 8 remaining, got {login2['backup_codes_remaining']}"

        # 5. Complete login with TOTP
        totp1 = pyotp.TOTP(secret)
        r5 = self._complete_2fa_login(api_client, login2, totp1.now())
        assert r5.status_code == status.HTTP_200_OK
        token2 = r5.data["access"]
        assert r5.data["user"]["email"] == user.email

        # 6. Check /auth/me/ → backup_codes_remaining should be 8
        me6 = self._get_me(token2)
        assert me6.status_code == status.HTTP_200_OK
        assert me6.data["two_factor_enabled"] is True
        assert (
            me6.data["backup_codes_remaining"] == 8
        ), f"Expected 8 backup codes via /me/, got {me6.data['backup_codes_remaining']}"

        # ════════════════════════════════════════════════════════════════
        # PHASE 2 ── Use backup codes (2 successful uses)
        # ════════════════════════════════════════════════════════════════

        # 7. Use backup code #1
        login7 = self._login_and_get_token(api_client, user)
        assert login7["backup_codes_remaining"] == 8
        r7 = self._complete_2fa_login(api_client, login7, backup_codes[0])
        assert r7.status_code == status.HTTP_200_OK, f"Backup code #1 should work. Got {r7.status_code}: {r7.data}"
        token7 = r7.data["access"]

        # 8. Check /auth/me/ → should be 7 now
        me8 = self._get_me(token7)
        assert (
            me8.data["backup_codes_remaining"] == 7
        ), f"Expected 7 after using one, got {me8.data['backup_codes_remaining']}"

        # 9. Use backup code #2
        login9 = self._login_and_get_token(api_client, user)
        assert login9["backup_codes_remaining"] == 7
        r9 = self._complete_2fa_login(api_client, login9, backup_codes[1])
        assert r9.status_code == status.HTTP_200_OK
        token9 = r9.data["access"]

        # 10. Check /auth/me/ → should be 6 now
        me10 = self._get_me(token9)
        assert (
            me10.data["backup_codes_remaining"] == 6
        ), f"Expected 6 after using two, got {me10.data['backup_codes_remaining']}"

        # ════════════════════════════════════════════════════════════════
        # PHASE 3 ── Lockout
        # ════════════════════════════════════════════════════════════════

        # 11. Login and trigger lockout with 3 failed backup code attempts
        login11 = self._login_and_get_token(api_client, user)
        assert login11["backup_codes_remaining"] == 6

        # First 2 wrong attempts → 400 with a remaining count; the 3rd reaches
        # the lockout limit and is rejected immediately with 429.
        for i in range(2):
            wrong_code = f"WRONG-{i:05d}"
            r = self._complete_2fa_login(api_client, login11, wrong_code)
            assert r.status_code == status.HTTP_400_BAD_REQUEST, f"Attempt {i+1} should return 400, got {r.status_code}"
            expected_remaining = 3 - i - 1
            if expected_remaining > 0:
                assert (
                    str(expected_remaining) in r.data["detail"].lower()
                ), f"Should mention {expected_remaining} remaining attempts"

        r = self._complete_2fa_login(api_client, login11, "WRONG-00002")
        assert (
            r.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        ), f"3rd wrong attempt should trigger lockout (429), got {r.status_code}"
        assert "try again in" in r.data["detail"].lower()

        # Verify lockout state in DB
        user.refresh_from_db()
        assert user.backup_code_failed_attempts == 3
        assert user.backup_code_locked_until is not None

        # 12. 4th attempt → 429 (locked out)
        # Login again to get a fresh user_id (lockout persists on the user)
        login12 = self._login_and_get_token(api_client, user)
        # The backup_codes_remaining should still be 6 (lockout doesn't affect the count)
        assert "backup_codes_remaining" in login12

        r12 = self._complete_2fa_login(api_client, login12, "WRONG-XXXXX")
        assert (
            r12.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        ), f"Locked out request should return 429, got {r12.status_code}"
        assert "try again in" in r12.data["detail"].lower()
        assert "try again in" in r12.data["detail"].lower()

        # 13. Even a valid backup code (#3) should be rejected during lockout
        login13 = self._login_and_get_token(api_client, user)
        r13 = self._complete_2fa_login(api_client, login13, backup_codes[2])
        assert (
            r13.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        ), f"Valid backup code during lockout should return 429, got {r13.status_code}"
        assert "try again in" in r13.data["detail"].lower()

        # 14. TOTP should still work during lockout
        login14 = self._login_and_get_token(api_client, user)
        totp14 = pyotp.TOTP(secret)
        r14 = self._complete_2fa_login(api_client, login14, totp14.now())
        assert (
            r14.status_code == status.HTTP_200_OK
        ), f"TOTP should work during backup code lockout, got {r14.status_code}"
        assert "access" in r14.data

        # ════════════════════════════════════════════════════════════════
        # PHASE 4 ── Regenerate + verify reset
        # ════════════════════════════════════════════════════════════════

        # 15. Use TOTP to get a fresh bearer token for regenerate
        login15 = self._login_and_get_token(api_client, user)
        totp15 = pyotp.TOTP(secret)
        r15 = self._complete_2fa_login(api_client, login15, totp15.now())
        assert r15.status_code == status.HTTP_200_OK
        token15 = r15.data["access"]

        # 16. Regenerate codes via HTTP
        regen_client = APIClient()
        regen_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token15}")
        regen_r = regen_client.post(
            AUTH_REGENERATE_BACKUP_CODES,
            {
                "password": "TestPass@1234",
            },
        )
        assert regen_r.status_code == status.HTTP_200_OK
        new_codes = regen_r.data["backup_codes"]
        assert len(new_codes) == 8

        # Verify lockout is reset in the DB
        user.refresh_from_db()
        assert user.backup_code_failed_attempts == 0
        assert user.backup_code_locked_until is None

        # Verify old backup codes are no longer in the DB
        old_hashed = hashlib.sha256(backup_codes[0].encode()).hexdigest()
        assert not TwoFactorBackupCode.objects.filter(
            user=user, hashed_code=old_hashed, used=False
        ).exists(), "Old backup code should no longer exist after regenerate"

        # 17. Check /auth/me/ → should be 8 again
        me17 = self._get_me(token15)
        assert (
            me17.data["backup_codes_remaining"] == 8
        ), f"Expected 8 after regenerate, got {me17.data['backup_codes_remaining']}"

        # 18. Login and use new backup code #1 → should succeed
        login18 = self._login_and_get_token(api_client, user)
        assert login18["backup_codes_remaining"] == 8
        r18 = self._complete_2fa_login(api_client, login18, new_codes[0])
        assert (
            r18.status_code == status.HTTP_200_OK
        ), f"New backup code should work after regenerate. Got {r18.status_code}: {r18.data}"
        token18 = r18.data["access"]

        # Verify count decreased via /auth/me/
        me18 = self._get_me(token18)
        assert (
            me18.data["backup_codes_remaining"] == 7
        ), f"Expected 7 after using one new code, got {me18.data['backup_codes_remaining']}"

        # 19. Old backup code #1 should be invalid (deleted by regenerate)
        login19 = self._login_and_get_token(api_client, user)
        r19 = self._complete_2fa_login(api_client, login19, backup_codes[0])
        assert (
            r19.status_code == status.HTTP_400_BAD_REQUEST
        ), f"Old backup code should be invalid after regenerate. Got {r19.status_code}: {r19.data}"
        assert "Invalid" in r19.data["detail"]

        # Verify lockout counter wasn't affected by the old-code attempt
        user.refresh_from_db()
        assert (
            user.backup_code_failed_attempts == 1
        ), "Old code attempt should increment counter but not trigger lockout yet"


# ─── Throttle / Rate-Limit Tests ─────────────────────────────────────────────


@pytest.mark.django_db
@pytest.mark.slow
class TestVerify2FALoginThrottle:
    """
    Tests for AuthVerify2FALoginThrottle (5 requests/minute per IP).

    IMPORTANT: These tests use a non-existent UUID as user_id to avoid
    tripping the backup-code lockout (3 failed attempts → 429).
    The Verify2FALoginView returns 400 ("Invalid user.") at the
    User.DoesNotExist check, which runs BEFORE any TOTP or backup-code
    logic. DRF's throttle check runs even earlier (before dispatch),
    so each request still counts against the 5/min limit without
    polluting the backup-code lockout counter.

    The autouse reset_cache fixture in conftest clears Django's cache
    between test classes, so throttle state starts fresh for each test.
    """

    NONEXISTENT_USER_ID = "00000000-0000-0000-0000-000000000000"

    def test_exceeding_5_per_minute_returns_429(self, api_client):
        """
        Sending more than 5 requests within the same minute should
        trigger DRF's AnonRateThrottle on the 6th request.
        """
        payload = {"user_id": self.NONEXISTENT_USER_ID, "code": "000000"}

        # First 5 requests should all return 400 (invalid user)
        for i in range(5):
            r = api_client.post(AUTH_VERIFY_2FA_LOGIN, payload)
            assert r.status_code == status.HTTP_400_BAD_REQUEST, f"Request {i+1} should return 400, got {r.status_code}"
            assert "Invalid user" in r.data["detail"]

        # 6th request should be throttled (429)
        r6 = api_client.post(AUTH_VERIFY_2FA_LOGIN, payload)
        assert (
            r6.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        ), f"6th request should be throttled (429), got {r6.status_code}: {r6.data}"
        assert "throttled" in r6.data["detail"].lower()

    def test_throttle_is_per_ip_independent(self, db):
        """
        Two different IP addresses should have independent throttle counters.
        Each IP gets 5 requests/minute independently.
        """
        payload = {"user_id": self.NONEXISTENT_USER_ID, "code": "000000"}

        # Make 5 requests from IP-A, then 6th should be throttled
        client_a = APIClient(REMOTE_ADDR="10.0.0.1")
        for i in range(5):
            r = client_a.post(AUTH_VERIFY_2FA_LOGIN, payload)
            assert (
                r.status_code == status.HTTP_400_BAD_REQUEST
            ), f"IP-A request {i+1} should return 400, got {r.status_code}"
        r_a6 = client_a.post(AUTH_VERIFY_2FA_LOGIN, payload)
        assert r_a6.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert "throttled" in r_a6.data["detail"].lower()

        # IP-B should still have its full quota — 5 requests then 6th throttled
        client_b = APIClient(REMOTE_ADDR="10.0.0.2")
        for i in range(5):
            r = client_b.post(AUTH_VERIFY_2FA_LOGIN, payload)
            assert (
                r.status_code == status.HTTP_400_BAD_REQUEST
            ), f"IP-B request {i+1} should return 400, got {r.status_code}"
        r_b6 = client_b.post(AUTH_VERIFY_2FA_LOGIN, payload)
        assert r_b6.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert "throttled" in r_b6.data["detail"].lower()

    def test_throttle_does_not_block_other_endpoints(self, api_client, user_with_2fa):
        """
        Throttle only applies to the verify-2fa-login endpoint.
        The login endpoint should still work after exhausting the
        verify-2fa-login rate limit.
        """
        user, _ = user_with_2fa
        payload = {"user_id": self.NONEXISTENT_USER_ID, "code": "000000"}

        # Exhaust the verify-2fa-login throttle
        for i in range(5):
            api_client.post(AUTH_VERIFY_2FA_LOGIN, payload)

        # 6th should be throttled
        r6 = api_client.post(AUTH_VERIFY_2FA_LOGIN, payload)
        assert r6.status_code == status.HTTP_429_TOO_MANY_REQUESTS

        # Login endpoint should still work (different rate limit)
        login = api_client.post(
            AUTH_LOGIN,
            {
                "email": user.email,
                "password": "TestPass@1234",
            },
        )
        assert login.status_code == status.HTTP_200_OK

    def test_throttle_not_triggered_within_limit(self, api_client):
        """
        Making fewer than 5 requests to verify-2fa-login per minute
        should never trigger the throttle.
        """
        payload = {"user_id": self.NONEXISTENT_USER_ID, "code": "000000"}

        # Make 3 requests — all should return 400 (not throttled)
        for i in range(3):
            r = api_client.post(AUTH_VERIFY_2FA_LOGIN, payload)
            assert r.status_code == status.HTTP_400_BAD_REQUEST, f"Request {i+1} should return 400, got {r.status_code}"
            assert "Invalid user" in r.data["detail"]


# ─── Login Throttle Tests ────────────────────────────────────────────────────


@pytest.mark.django_db
@pytest.mark.slow
class TestAuthLoginThrottle:
    """
    Tests for AuthLoginAnonThrottle (10 requests/minute per IP).

    These tests use an unknown email to trigger 401 responses, which
    count against the throttle without affecting any per-account lockout
    (django-axes is disabled in test settings).

    The autouse reset_cache fixture in conftest clears Django's cache
    between test classes, so throttle state starts fresh for each test.
    """

    UNKNOWN_EMAIL = "unknown@school.edu"
    PAYLOAD = {"email": UNKNOWN_EMAIL, "password": "WrongPass@1234"}

    def test_exceeding_10_per_minute_returns_429(self, api_client):
        """
        Sending more than 10 login requests within the same minute should
        trigger DRF's AnonRateThrottle on the 11th request.
        """
        # First 10 requests should all return 401 (invalid credentials)
        for i in range(10):
            r = api_client.post(AUTH_LOGIN, self.PAYLOAD)
            assert (
                r.status_code == status.HTTP_401_UNAUTHORIZED
            ), f"Request {i+1} should return 401, got {r.status_code}"

        # 11th request should be throttled (429)
        r11 = api_client.post(AUTH_LOGIN, self.PAYLOAD)
        assert (
            r11.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        ), f"11th request should be throttled (429), got {r11.status_code}: {r11.data}"
        assert "throttled" in r11.data["detail"].lower()

    def test_throttle_is_per_ip_independent(self, db):
        """
        Two different IP addresses should have independent throttle counters.
        Each IP gets 10 requests/minute independently.
        """
        # Make 10 requests from IP-A, then 11th should be throttled
        client_a = APIClient(REMOTE_ADDR="10.0.0.1")
        for i in range(10):
            r = client_a.post(AUTH_LOGIN, self.PAYLOAD)
            assert (
                r.status_code == status.HTTP_401_UNAUTHORIZED
            ), f"IP-A request {i+1} should return 401, got {r.status_code}"
        r_a11 = client_a.post(AUTH_LOGIN, self.PAYLOAD)
        assert r_a11.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert "throttled" in r_a11.data["detail"].lower()

        # IP-B should still have its full quota — 10 requests then 11th throttled
        client_b = APIClient(REMOTE_ADDR="10.0.0.2")
        for i in range(10):
            r = client_b.post(AUTH_LOGIN, self.PAYLOAD)
            assert (
                r.status_code == status.HTTP_401_UNAUTHORIZED
            ), f"IP-B request {i+1} should return 401, got {r.status_code}"
        r_b11 = client_b.post(AUTH_LOGIN, self.PAYLOAD)
        assert r_b11.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert "throttled" in r_b11.data["detail"].lower()

    def test_throttle_not_triggered_within_limit(self, api_client):
        """
        Making fewer than 10 login requests per minute should never
        trigger the throttle.
        """
        # Make 5 requests — all should return 401 (not throttled)
        for i in range(5):
            r = api_client.post(AUTH_LOGIN, self.PAYLOAD)
            assert (
                r.status_code == status.HTTP_401_UNAUTHORIZED
            ), f"Request {i+1} should return 401, got {r.status_code}"

    def test_valid_login_also_counts_towards_throttle(self, api_client, user):
        """
        Successful logins also count towards the rate limit.
        After 10 total login requests (valid or invalid), the 11th
        should be throttled.
        """
        # 9 requests with wrong credentials
        for i in range(9):
            r = api_client.post(AUTH_LOGIN, self.PAYLOAD)
            assert r.status_code == status.HTTP_401_UNAUTHORIZED

        # 10th request with valid credentials — should succeed
        r10 = api_client.post(
            AUTH_LOGIN,
            {
                "email": user.email,
                "password": "TestPass@1234",
            },
        )
        assert r10.status_code == status.HTTP_200_OK

        # 11th request should be throttled (429)
        r11 = api_client.post(AUTH_LOGIN, self.PAYLOAD)
        assert r11.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert "throttled" in r11.data["detail"].lower()

    def test_throttle_does_not_affect_other_endpoints(self, api_client, user):
        """
        Throttle only applies to the login endpoint.
        Other endpoints (like verify-2fa-login) should still work after
        exhausting the login rate limit.
        """
        # Exhaust the login throttle
        for i in range(10):
            api_client.post(AUTH_LOGIN, self.PAYLOAD)

        # 11th should be throttled
        r11 = api_client.post(AUTH_LOGIN, self.PAYLOAD)
        assert r11.status_code == status.HTTP_429_TOO_MANY_REQUESTS

        # A different endpoint should still work
        r = api_client.post(
            AUTH_VERIFY_2FA_LOGIN,
            {
                "user_id": "00000000-0000-0000-0000-000000000000",
                "code": "000000",
            },
        )
        assert r.status_code == status.HTTP_400_BAD_REQUEST


# ─── Combined Throttle + Backup Code Flow ────────────────────────────────────


@pytest.mark.django_db
@pytest.mark.slow
class TestCombinedThrottleAndBackupFlow:
    """
    Integration test that exercises the full backup code flow while also
    verifying that both DRF throttles (AuthLoginAnonThrottle at 10/min and
    AuthVerify2FALoginThrottle at 5/min) apply correctly and independently.

    The flow:
      1. Full backup code setup and usage
      2. Backup code lockout (3 wrong → 429 lockout)
      3. TOTP still works during lockout
      4. Exhaust verify-2fa-login throttle (non-existent user_id to avoid lockout)
      5. Exhaust login throttle (unknown email)
      6. Verify each throttle only affects its own endpoint
    """

    NONEXISTENT_USER_ID = "00000000-0000-0000-0000-000000000000"
    UNKNOWN_EMAIL = "unknown@school.edu"

    def _login(self, api_client, email, password):
        return api_client.post(AUTH_LOGIN, {"email": email, "password": password})

    def _verify_2fa(self, api_client, user_id, code):
        return api_client.post(
            AUTH_VERIFY_2FA_LOGIN,
            {
                "user_id": user_id,
                "code": code,
            },
        )

    def test_combined_flow(self, api_client, user, lifted_2fa_throttles):
        """
        Complete combined flow covering backup codes, lockout, TOTP, and both throttles.
        """

        # ════════════════════════════════════════════════════════════════════
        # PHASE 1 ── Setup 2FA
        # ════════════════════════════════════════════════════════════════════

        # Login → token
        login1 = self._login(api_client, user.email, "TestPass@1234")
        assert login1.status_code == status.HTTP_200_OK
        token1 = login1.data["access"]

        # Setup 2FA → secret + 8 backup codes
        setup_client = APIClient()
        setup_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token1}")
        setup_r = setup_client.post(AUTH_SETUP_2FA)
        assert setup_r.status_code == status.HTTP_200_OK
        secret = setup_r.data["secret"]
        backup_codes = setup_r.data["backup_codes"]
        assert len(backup_codes) == 8

        # Enable 2FA with TOTP
        totp = pyotp.TOTP(secret)
        verify_r = setup_client.post(AUTH_VERIFY_2FA, {"code": totp.now()})
        assert verify_r.status_code == status.HTTP_200_OK

        user.refresh_from_db()
        assert user.two_factor_enabled is True

        # ════════════════════════════════════════════════════════════════════
        # PHASE 2 ── Use backup codes + trigger lockout + TOTP still works
        # ════════════════════════════════════════════════════════════════════

        # Login → requires_2fa with backup_codes_remaining: 8
        login2 = self._login(api_client, user.email, "TestPass@1234")
        assert login2.data["requires_2fa"] is True
        assert login2.data["backup_codes_remaining"] == 8
        user_id = login2.data["user_id"]

        # Use backup code #1 → success
        r = self._verify_2fa(api_client, user_id, backup_codes[0])
        assert r.status_code == status.HTTP_200_OK
        token2 = r.data["access"]

        # Check count decreased
        me = APIClient()
        me.credentials(HTTP_AUTHORIZATION=f"Bearer {token2}")
        assert me.get(AUTH_ME).data["backup_codes_remaining"] == 7

        # Use backup code #2 → success
        login3 = self._login(api_client, user.email, "TestPass@1234")
        r = self._verify_2fa(api_client, login3.data["user_id"], backup_codes[1])
        assert r.status_code == status.HTTP_200_OK
        token3 = r.data["access"]

        # Check count decreased again
        me2 = APIClient()
        me2.credentials(HTTP_AUTHORIZATION=f"Bearer {token3}")
        assert me2.get(AUTH_ME).data["backup_codes_remaining"] == 6

        # ── Trigger backup code lockout ───────────────────────────────────────

        # First 2 wrong attempts → 400 with remaining count; the 3rd reaches
        # the lockout limit and is rejected immediately with 429.
        login4 = self._login(api_client, user.email, "TestPass@1234")
        uid4 = login4.data["user_id"]

        for i in range(2):
            r = self._verify_2fa(api_client, uid4, f"WRONG-{i:05d}")
            assert r.status_code == status.HTTP_400_BAD_REQUEST
        r = self._verify_2fa(api_client, uid4, "WRONG-00002")
        assert r.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert "try again in" in r.data["detail"].lower()

        # 4th attempt → 429 lockout (NOT throttle)
        r = self._verify_2fa(api_client, uid4, "WRONG-XXXXX")
        assert r.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert "try again in" in r.data["detail"].lower(), "Should be backup-code lockout, not throttle"
        assert "try again in" in r.data["detail"].lower()

        # Even a valid backup code (#3) rejected during lockout → 429
        login5 = self._login(api_client, user.email, "TestPass@1234")
        r = self._verify_2fa(api_client, login5.data["user_id"], backup_codes[2])
        assert r.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert "try again in" in r.data["detail"].lower()

        # ── TOTP still works during lockout ───────────────────────────────────

        login6 = self._login(api_client, user.email, "TestPass@1234")
        totp_now = pyotp.TOTP(secret).now()
        r = self._verify_2fa(api_client, login6.data["user_id"], totp_now)
        assert r.status_code == status.HTTP_200_OK, "TOTP should work during backup code lockout"
        assert "access" in r.data

        # ════════════════════════════════════════════════════════════════════
        # PHASES 3–5 ── Exhaust both throttles at their real rates
        # ════════════════════════════════════════════════════════════════════
        # The lockout phases above ran with lifted per-IP rates; these phases
        # restore the real rates and start each throttle with a clean history.
        from django.core.cache import cache
        from rest_framework.throttling import SimpleRateThrottle

        real_rates = dict(SimpleRateThrottle.THROTTLE_RATES)
        real_rates.update(auth_verify_2fa_login="5/minute", auth_login="10/minute")
        with _patch_throttle_rates(real_rates):
            cache.clear()

            # Use non-existent user_id so requests fail at User.DoesNotExist
            # without triggering backup-code logic or lockout.
            throttle_payload = {
                "user_id": self.NONEXISTENT_USER_ID,
                "code": "000000",
            }

            # 5 requests → all return 400 (invalid user)
            for i in range(5):
                r = api_client.post(AUTH_VERIFY_2FA_LOGIN, throttle_payload)
                assert (
                    r.status_code == status.HTTP_400_BAD_REQUEST
                ), f"Verify-throttle request {i+1} should return 400, got {r.status_code}"
                assert "Invalid user" in r.data["detail"]

            # 6th → 429 throttle (NOT lockout)
            r = api_client.post(AUTH_VERIFY_2FA_LOGIN, throttle_payload)
            assert (
                r.status_code == status.HTTP_429_TOO_MANY_REQUESTS
            ), f"6th verify request should be throttled (429), got {r.status_code}: {r.data}"
            assert "throttled" in r.data["detail"].lower(), "Should be DRF throttle, not backup-code lockout"

            # Verify login endpoint still works (different throttle scope)
            login7 = self._login(api_client, user.email, "TestPass@1234")
            assert login7.status_code == status.HTTP_200_OK

            # ── PHASE 4 ── Exhaust login throttle (10/min) ──────────────────
            # Clear only the login-scope history; the verify history from Phase 3
            # must survive for the Phase 5 isolation check.
            cache.delete("throttle_auth_login_127.0.0.1")

            # 10 requests with unknown email → 401
            for i in range(10):
                r = self._login(api_client, self.UNKNOWN_EMAIL, "WrongPass@1234")
                assert (
                    r.status_code == status.HTTP_401_UNAUTHORIZED
                ), f"Login request {i+1} should return 401, got {r.status_code}"

            # 11th → 429 login throttle
            r = self._login(api_client, self.UNKNOWN_EMAIL, "WrongPass@1234")
            assert (
                r.status_code == status.HTTP_429_TOO_MANY_REQUESTS
            ), f"11th login should be throttled (429), got {r.status_code}: {r.data}"
            assert "throttled" in r.data["detail"].lower()

            # ── PHASE 5 ── Verify endpoint isolation ────────────────────────
            # Login throttle exhausted, but verify-2fa-login is a different
            # scope: it should still be throttled from Phase 3 (same minute),
            # proving the two throttles are independent.
            r = api_client.post(AUTH_VERIFY_2FA_LOGIN, throttle_payload)
            assert r.status_code == status.HTTP_429_TOO_MANY_REQUESTS
            assert "throttled" in r.data["detail"].lower()

        user.refresh_from_db()
        assert user.backup_code_failed_attempts == 3, "Lockout state should be unchanged by throttle-only requests"


# ─── Axes Brute-Force Lockout Tests ──────────────────────────────────────────


@pytest.mark.django_db
@pytest.mark.slow
@pytest.mark.slow_axes
class TestAxesLockout:
    """
    Tests for django-axes brute-force lockout (5 failed logins → 30 min ban).

    Axes is disabled globally in conftest (AXES_ENABLED = False) so these
    tests use @override_settings from django.test.utils to enable it per
    test method. Each test starts with fresh axes state because axes uses
    the database, and each test runs in its own transaction.
    """

    @override_settings(AXES_ENABLED=True)
    def test_lockout_after_5_failed_login_attempts(self, api_client, user):
        """
        After 5 failed login attempts with the correct email, the 6th
        attempt should be blocked by axes with a 403 lockout response.
        """
        from axes.models import AccessAttempt

        payload = {"email": user.email, "password": "WrongPass@1234"}

        # 5 failed attempts → each returns 401
        for i in range(5):
            r = api_client.post(AUTH_LOGIN, payload)
            assert (
                r.status_code == status.HTTP_401_UNAUTHORIZED
            ), f"Attempt {i+1} should return 401, got {r.status_code}"

        # 6th attempt → 403 (axes lockout)
        r = api_client.post(AUTH_LOGIN, payload)
        assert (
            r.status_code == status.HTTP_403_FORBIDDEN
        ), f"6th attempt should be locked out (403), got {r.status_code}"

        # Verify the response contains a lockout message
        content = r.content.decode("utf-8", errors="replace").lower()
        assert "locked" in content or "attempt" in content, "Lockout response should mention locked or attempts"

        # Clean up axes state for this test to avoid affecting other tests
        AccessAttempt.objects.filter(ip_address="127.0.0.1").delete()

    @override_settings(AXES_ENABLED=True)
    def test_different_user_not_affected(self, api_client, user, db):
        """
        Axes lockout is per-user (by default, per username+IP).
        A different user should still be able to log in even after
        one user has been locked out.
        """
        from tests.factories import UserFactory

        other_user = UserFactory(
            school=user.school,
            email="other@school.edu",
            role="student",
        )

        payload = {"email": user.email, "password": "WrongPass@1234"}

        # Lock out user1
        for i in range(5):
            api_client.post(AUTH_LOGIN, payload)
        r = api_client.post(AUTH_LOGIN, payload)
        assert r.status_code == status.HTTP_403_FORBIDDEN

        # A different user should still be able to log in
        r2 = api_client.post(
            AUTH_LOGIN,
            {
                "email": other_user.email,
                "password": "TestPass@1234",
            },
        )
        assert (
            r2.status_code == status.HTTP_200_OK
        ), f"Different user should still be able to login, got {r2.status_code}"
        assert "access" in r2.data

        reset(ip="127.0.0.1")

    @override_settings(AXES_ENABLED=True)
    def test_correct_password_during_lockout_still_blocked(self, api_client, user):
        """
        Even with the correct password, a locked-out user should
        still receive a 403 lockout response until the cooldown expires.
        """

        # Trigger lockout with wrong password
        payload_wrong = {"email": user.email, "password": "WrongPass@1234"}
        for i in range(5):
            api_client.post(AUTH_LOGIN, payload_wrong)

        # Correct password during lockout should still get 403
        r = api_client.post(
            AUTH_LOGIN,
            {
                "email": user.email,
                "password": "TestPass@1234",
            },
        )
        assert r.status_code == status.HTTP_403_FORBIDDEN, "Correct password should still be blocked during lockout"

        reset(ip="127.0.0.1")
