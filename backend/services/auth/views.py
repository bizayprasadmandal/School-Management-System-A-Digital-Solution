"""
Auth Service — Login, profile, password management, token views + full ViewSet coverage.
"""

import hashlib
import logging
import secrets
from datetime import timedelta

from core.pagination import StandardResultsSetPagination
from core.permissions import IsSchoolAdmin, IsSchoolMember, IsSuperAdmin
from core.throttles import (
    AuthLoginAnonThrottle,
    AuthPasswordResetConfirmThrottle,
    AuthPasswordResetThrottle,
    AuthVerify2FALoginThrottle,
)
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, parsers, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from services.communication.services import send_in_app_notification

from .models import (
    APIKey,
    APIUsageLog,
    AuditLog,
    AuditReportSchedule,
    AuthWebhook,
    ComplianceRecord,
    ConsentRecord,
    DataDeletionRequest,
    DataExportRequest,
    DeviceManagement,
    DomainVerification,
    EmailVerificationToken,
    IPGeolocationCache,
    IPWhitelist,
    LoginAttempt,
    LoginHistory,
    MFAMethod,
    MFAVerification,
    OAuthProvider,
    OAuthToken,
    PasswordHistory,
    PasswordPolicy,
    PasswordResetToken,
    Permission,
    Role,
    RolePermission,
    School,
    SchoolFeatureFlag,
    SecurityNotificationPreference,
    SecurityPolicy,
    SessionPolicy,
    SessionToken,
    SSOConfiguration,
    TwoFactorBackupCode,
    User,
    UserActivity,
    UserRole,
    UserRoleAssignment,
    UserSession,
    UserSessionHistory,
    UserTrustScore,
    WebhookDelivery,
)
from .serializers import (
    APIKeySerializer,
    APIUsageLogSerializer,
    AuditLogSerializer,
    AuditReportScheduleSerializer,
    AuthWebhookSerializer,
    ComplianceRecordSerializer,
    ConsentRecordSerializer,
    CustomTokenObtainPairSerializer,
    DataDeletionRequestSerializer,
    DataExportRequestSerializer,
    DeviceManagementSerializer,
    DomainVerificationSerializer,
    EmailVerificationTokenSerializer,
    IPGeolocationCacheSerializer,
    IPWhitelistSerializer,
    LoginAttemptSerializer,
    LoginHistorySerializer,
    MFAMethodSerializer,
    MFAVerificationSerializer,
    OAuthProviderSerializer,
    OAuthTokenSerializer,
    PasswordHistorySerializer,
    PasswordPolicySerializer,
    PasswordResetTokenSerializer,
    PermissionSerializer,
    PlatformDashboardSerializer,
    RolePermissionSerializer,
    RoleSerializer,
    SchoolAdminSerializer,
    SchoolFeatureFlagSerializer,
    SchoolSerializer,
    SecurityNotificationPreferenceSerializer,
    SecurityPolicySerializer,
    SessionPolicySerializer,
    SessionTokenSerializer,
    SSOConfigurationSerializer,
    TwoFactorBackupCodeSerializer,
    UserActivitySerializer,
    UserDirectorySerializer,
    UserProfileSerializer,
    UserRoleSerializer,
    UserSessionHistorySerializer,
    UserSessionSerializer,
    UserTrustScoreSerializer,
    WebhookDeliverySerializer,
    serialize_login_user,
)

logger = logging.getLogger(__name__)

BACKUP_CODE_COUNT = 8


def _is_allowed_origin(url: str, fallback_url: str) -> bool:
    """
    True only when ``url`` is an http(s) URL whose origin (scheme + netloc)
    matches the application's own origin. Used to validate client-supplied
    redirect/verification URLs before embedding them in emails, so an attacker
    cannot inject a link to a foreign/phishing origin into platform email.
    """
    try:
        from urllib.parse import urlparse

        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            return False
        # Any loopback origin is an application origin — dev servers (Vite,
        # CRA, etc.) run on localhost with arbitrary ports, so require only
        # that the host is this machine rather than an exact port match.
        hostname = (parsed.hostname or "").lower()
        if hostname in ("localhost", "127.0.0.1", "::1"):
            return True
        allowed = urlparse(fallback_url)
        return parsed.scheme == allowed.scheme and parsed.netloc == allowed.netloc
    except (ValueError, TypeError):
        return False


def _get_client_ip(request):
    """Extract the client IP from the request, respecting proxies."""
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    return forwarded.split(",")[0].strip() if forwarded else request.META.get("REMOTE_ADDR")


def _generate_backup_codes(user, count=BACKUP_CODE_COUNT):
    """
    Generate `count` random backup codes for the given user.
    Stores SHA-256 hashed versions in the database.
    Returns the list of plain-text codes to show the user once.
    """
    # Invalidate any existing unused codes for this user
    TwoFactorBackupCode.objects.filter(user=user, used=False).delete()

    plain_codes = []
    codes_to_create = []
    for _ in range(count):
        # Format: XXXXX-XXXXX (2 groups of 5 alphanumeric chars)
        raw = secrets.token_hex(5).upper()[:5] + "-" + secrets.token_hex(5).upper()[:5]
        plain_codes.append(raw)
        hashed = hashlib.sha256(raw.encode()).hexdigest()
        codes_to_create.append(TwoFactorBackupCode(user=user, hashed_code=hashed))

    TwoFactorBackupCode.objects.bulk_create(codes_to_create)
    # Reset lockout state since the user now has fresh codes
    _reset_backup_code_lockout(user)
    return plain_codes


BACKUP_CODE_LOCKOUT_LIMIT = 3
BACKUP_CODE_LOCKOUT_DURATION = timedelta(minutes=30)


def _check_backup_code_lockout(user):
    """
    Check if the user is currently locked out from backup code verification.
    Returns a tuple (is_locked_out, remaining_seconds) where remaining_seconds
    is the number of seconds until the lockout expires.
    """
    if user.backup_code_locked_until and timezone.now() < user.backup_code_locked_until:
        remaining = int((user.backup_code_locked_until - timezone.now()).total_seconds())
        return True, max(remaining, 1)
    return False, 0


def _record_failed_backup_code_attempt(user):
    """
    Increment the failed backup code attempt counter.
    If the counter reaches the lockout limit, set the lockout timer.
    """
    user.backup_code_failed_attempts += 1
    if user.backup_code_failed_attempts >= BACKUP_CODE_LOCKOUT_LIMIT:
        user.backup_code_locked_until = timezone.now() + BACKUP_CODE_LOCKOUT_DURATION
    user.save(update_fields=["backup_code_failed_attempts", "backup_code_locked_until"])


def _reset_backup_code_lockout(user):
    """Reset failed attempt counter and lockout timer for a user."""
    if user.backup_code_failed_attempts > 0 or user.backup_code_locked_until is not None:
        user.backup_code_failed_attempts = 0
        user.backup_code_locked_until = None
        user.save(update_fields=["backup_code_failed_attempts", "backup_code_locked_until"])


def _check_backup_code(user, code):
    """
    Check if `code` is a valid, unused backup code for the user.
    If valid, marks it as used and returns True.
    """
    hashed = hashlib.sha256(code.encode()).hexdigest()
    try:
        bc = TwoFactorBackupCode.objects.get(user=user, hashed_code=hashed, used=False)
        bc.used = True
        bc.save(update_fields=["used"])
        return True
    except TwoFactorBackupCode.DoesNotExist:
        return False


class LoginView(TokenObtainPairView):
    """
    Authenticate with email + password. Returns JWT access/refresh pair
    plus full user profile in the response body.
    If the user has 2FA enabled, returns a partial token and requires
    a follow-up call to Verify2FAView with the TOTP code.
    """

    serializer_class = CustomTokenObtainPairSerializer
    throttle_classes = [AuthLoginAnonThrottle]

    def post(self, request, *args, **kwargs):
        email = request.data.get("email", "")
        user = User.objects.filter(email=email).first() if email else None

        # 2FA users must pass a TOTP/backup-code step before any JWT is minted.
        # Issuing tokens here and discarding them would churn refresh-token
        # state on every login attempt, so authenticate (Axes lockout still
        # applies) and return only the challenge.
        if user and user.two_factor_enabled and user.two_factor_secret:
            from django.contrib.auth import authenticate

            authenticated = authenticate(
                request=request,
                username=email,
                password=request.data.get("password", ""),
            )
            if authenticated is None:
                return Response(
                    {"detail": "No active account found with the given credentials"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            return Response(
                {
                    "requires_2fa": True,
                    "user_id": str(user.id),
                    "backup_codes_remaining": user.backup_codes.filter(used=False).count(),
                    "detail": ("2FA is enabled. Please provide your TOTP code " "via /auth/verify-2fa/"),
                },
                status=200,
            )

        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            user = User.objects.get(email=email)

            user.last_login_ip = _get_client_ip(request)
            user.save(update_fields=["last_login_ip"])
            AuditLog.objects.create(
                school=user.school,
                user=user,
                action="login",
                resource_type="user",
                resource_id=str(user.id),
                ip_address=_get_client_ip(request),
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
            )

            # ── In-app notification for unverified email ──────────────
            if not user.email_verified:
                send_in_app_notification.delay(
                    user_id=str(user.id),
                    title="Email not verified",
                    body=(
                        "Your email address has not been verified yet. "
                        "Some features are restricted until you verify. "
                        "Go to your profile settings to send a verification link."
                    ),
                    reference_type="email_verification",
                )

        return response


class LogoutView(APIView):
    """Blacklist the refresh token to invalidate the session."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"detail": "Refresh token required."}, status=400)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Logged out successfully."})
        except Exception as e:
            logger.warning("Logout failed: %s", str(e)[:100])
            return Response({"detail": "Invalid or expired token."}, status=400)


class ProfileView(generics.RetrieveUpdateAPIView):
    """Get/update the authenticated user's own profile."""

    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def perform_update(self, serializer):
        user = serializer.save()
        # Update auth store will refetch on next profile load
        AuditLog.objects.create(
            school=user.school,
            user=user,
            action="profile_update",
            resource_type="user",
            resource_id=str(user.id),
            ip_address=self.request.META.get("REMOTE_ADDR"),
        )


class UploadAvatarView(APIView):
    """Upload or remove the authenticated user's avatar image."""

    permission_classes = [IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]

    def post(self, request):
        user = request.user
        file = request.FILES.get("avatar")
        if file:
            user.avatar = file
            user.save(update_fields=["avatar"])
            return Response(
                {
                    "avatar": user.avatar.url if user.avatar else None,
                    "detail": "Avatar updated successfully.",
                }
            )
        return Response({"detail": "No file provided. Send a file with key 'avatar'."}, status=400)

    def delete(self, request):
        user = request.user
        if user.avatar:
            user.avatar.delete()
            user.avatar = None
            user.save(update_fields=["avatar"])
        return Response({"detail": "Avatar removed."})


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        old_password = request.data.get("old_password", "")
        new_password = request.data.get("new_password", "")

        if not user.check_password(old_password):
            return Response({"old_password": ["Incorrect current password."]}, status=400)

        try:
            validate_password(new_password, user)
        except Exception as e:
            return Response({"new_password": list(e)}, status=400)

        user.set_password(new_password)
        user.save()

        AuditLog.objects.create(
            school=user.school,
            user=user,
            action="password_change",
            resource_type="user",
            resource_id=str(user.id),
            ip_address=request.META.get("REMOTE_ADDR"),
        )
        return Response({"detail": "Password updated successfully."})


class RequestPasswordResetView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AuthPasswordResetThrottle]

    def post(self, request):
        email = request.data.get("email", "").strip().lower()
        if not email:
            return Response({"email": ["Email is required."]}, status=400)

        # Always return success (don't reveal if email exists)
        try:
            user = User.objects.get(email=email, is_active=True)
            token_str = secrets.token_urlsafe(48)
            PasswordResetToken.objects.filter(user=user, used=False).update(used=True)
            PasswordResetToken.objects.create(
                user=user,
                token=hashlib.sha256(token_str.encode()).hexdigest(),
                expires_at=timezone.now() + timedelta(hours=2),
            )
            # Send email async
            from django.conf import settings
            from services.communication.tasks import send_email_notification

            frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:3000")
            # Client-supplied reset URLs must match the app's own origin — never
            # embed an arbitrary link (phishing/link-injection) in reset emails.
            reset_url = request.data.get("reset_url", "")
            if reset_url and not _is_allowed_origin(reset_url, frontend_url):
                return Response(
                    {"reset_url": ["reset_url must use the application's own origin."]},
                    status=400,
                )
            reset_url = reset_url or f"{frontend_url}/reset-password/{token_str}"
            send_email_notification.delay(
                user_id=str(user.id),
                subject="Password Reset Request",
                body=f"Click here to reset your password: {reset_url}",
            )
        except User.DoesNotExist:
            pass

        return Response({"detail": "If an account with that email exists, a reset link has been sent."})


class ConfirmPasswordResetView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AuthPasswordResetConfirmThrottle]

    def post(self, request):
        token_str = request.data.get("token", "")
        new_password = request.data.get("new_password", "")

        try:
            reset_token = PasswordResetToken.objects.select_related("user").get(
                token=hashlib.sha256(token_str.encode()).hexdigest(), used=False
            )
        except PasswordResetToken.DoesNotExist:
            return Response({"detail": "Invalid or expired reset link."}, status=400)

        if reset_token.is_expired:
            return Response({"detail": "This reset link has expired. Please request a new one."}, status=400)

        user = reset_token.user
        try:
            validate_password(new_password, user)
        except Exception as e:
            return Response({"new_password": list(e)}, status=400)

        user.set_password(new_password)
        user.save()
        reset_token.used = True
        reset_token.save()

        return Response({"detail": "Password reset successfully. You can now log in."})


class Setup2FAView(APIView):
    """
    Generate a TOTP secret for the authenticated user and return the
    provisioning URI (for QR code), the raw secret, and backup codes.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        import pyotp

        user = request.user
        secret = pyotp.random_base32()
        user.two_factor_secret = secret
        issuer = getattr(user.school, "name", "EduSphere SMS")
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(user.email, issuer_name=issuer)
        user.two_factor_enabled = False  # Not enabled until verified
        user.save(update_fields=["two_factor_secret", "two_factor_enabled"])

        # Generate backup codes immediately (shown before TOTP verification)
        backup_codes = _generate_backup_codes(user)

        return Response(
            {
                "secret": secret,
                "provisioning_uri": provisioning_uri,
                "backup_codes": backup_codes,
                "detail": (
                    "Scan the QR code with your authenticator app, then call "
                    "/auth/verify-2fa/ to enable. Save your backup codes in a safe place."
                ),
            }
        )


class Verify2FAView(APIView):
    """Verify a TOTP code and enable 2FA for the user."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        import pyotp

        user = request.user
        code = request.data.get("code", "")
        if not user.two_factor_secret:
            return Response({"detail": "2FA not set up. Call /auth/setup-2fa/ first."}, status=400)
        totp = pyotp.TOTP(user.two_factor_secret)
        if totp.verify(code, valid_window=1):
            user.two_factor_enabled = True
            user.save(update_fields=["two_factor_enabled"])

            # Generate backup codes if they don't already exist
            if not TwoFactorBackupCode.objects.filter(user=user, used=False).exists():
                backup_codes = _generate_backup_codes(user)
                return Response(
                    {
                        "detail": "2FA enabled successfully.",
                        "backup_codes": backup_codes,
                    }
                )

            return Response({"detail": "2FA enabled successfully."})
        return Response({"detail": "Invalid TOTP code."}, status=400)


class Disable2FAView(APIView):
    """Disable 2FA for the authenticated user and clean up backup codes."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        current_password = request.data.get("password", "")
        if not user.check_password(current_password):
            return Response({"detail": "Invalid password."}, status=400)
        user.two_factor_enabled = False
        user.two_factor_secret = ""
        user.save(update_fields=["two_factor_enabled", "two_factor_secret"])
        # Clean up all backup codes and reset lockout state
        TwoFactorBackupCode.objects.filter(user=user).delete()
        _reset_backup_code_lockout(user)
        return Response({"detail": "2FA disabled."})


class Verify2FALoginView(APIView):
    """
    Complete login with TOTP code or backup code after initial
    password verification (requires_2fa=True step).
    Rate-limited to 5 requests/minute per IP.
    """

    permission_classes = [AllowAny]
    throttle_classes = [AuthVerify2FALoginThrottle]

    def _issue_jwt(self, user, request):
        """Issue JWT tokens and send verification notification if needed."""
        from rest_framework_simplejwt.tokens import RefreshToken

        refresh = RefreshToken.for_user(user)

        if not user.email_verified:
            send_in_app_notification.delay(
                user_id=str(user.id),
                title="Email not verified",
                body=(
                    "Your email address has not been verified yet. "
                    "Some features are restricted until you verify. "
                    "Go to your profile settings to send a verification link."
                ),
                reference_type="email_verification",
            )

        # Match the user payload shape of the regular login response
        # (CustomTokenObtainPairSerializer) so the frontend auth store and
        # welcome toast receive first_name/avatar/email_verified/school.
        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": serialize_login_user(user),
            }
        )

    def post(self, request):
        user_id = request.data.get("user_id", "")
        code = request.data.get("code", "")
        try:
            user = User.objects.get(id=user_id, is_active=True)
        except User.DoesNotExist:
            return Response({"detail": "Invalid user."}, status=400)

        if not user.two_factor_enabled or not user.two_factor_secret:
            return Response({"detail": "2FA not enabled for this user."}, status=400)

        # Try TOTP first
        import pyotp

        totp = pyotp.TOTP(user.two_factor_secret)
        if totp.verify(code, valid_window=1):
            return self._issue_jwt(user, request)

        # Fall back to backup code
        # Check lockout first
        is_locked, remaining = _check_backup_code_lockout(user)
        if is_locked:
            return Response(
                {
                    "detail": ("Too many failed backup code attempts. " f"Try again in {remaining} seconds."),
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        if _check_backup_code(user, code):
            # Successful backup code use — reset lockout counter
            _reset_backup_code_lockout(user)
            return self._issue_jwt(user, request)

        # Failed backup code attempt — record it
        _record_failed_backup_code_attempt(user)

        attempts_left = BACKUP_CODE_LOCKOUT_LIMIT - user.backup_code_failed_attempts
        if attempts_left <= 0:
            return Response(
                {
                    "detail": (
                        "Too many failed backup code attempts. You are temporarily "
                        "locked out. Try again in 30 minutes or use your authenticator app."
                    ),
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        return Response(
            {
                "detail": (
                    f"Invalid verification code. {attempts_left} backup code attempt"
                    f"{'s' if attempts_left != 1 else ''} remaining before lockout."
                ),
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class SendEmailVerificationView(APIView):
    """
    Generate a verification token and send an email with the verification link.
    The user must be authenticated but have email_verified=False.
    """

    permission_classes = [IsAuthenticated]
    throttle_classes = [AuthPasswordResetThrottle]  # Reuse: 1 request per X time

    def post(self, request):
        from services.communication.tasks import send_email_notification

        from .models import EmailVerificationToken
        from .serializers import SendEmailVerificationSerializer

        serializer = SendEmailVerificationSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        user = request.user
        email = serializer.validated_data.get("email") or user.email

        # Invalidate any existing unused tokens for this user
        EmailVerificationToken.objects.filter(user=user, used=False, email=email).update(used=True)

        # Create new token (expires in 24 hours)
        token_str = secrets.token_urlsafe(48)
        EmailVerificationToken.objects.create(
            user=user,
            email=email,
            token=token_str,
            expires_at=timezone.now() + timedelta(hours=24),
        )

        # Build verification link — default to frontend URL
        from django.conf import settings

        frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:3000")
        # Client-supplied base URLs must match the app's own origin — never
        # embed an arbitrary link (phishing/link-injection) in verification
        # emails.
        base_url = request.data.get("verification_base_url", "")
        if base_url and not _is_allowed_origin(base_url, frontend_url):
            return Response(
                {"verification_base_url": ["verification_base_url must use the application's own origin."]},
                status=400,
            )
        base_url = base_url or frontend_url
        verify_url = f"{base_url}/verify-email/{token_str}"

        # Send email asynchronously
        send_email_notification.delay(
            user_id=str(user.id),
            subject="Verify Your Email Address — EduSphere SMS",
            body=(
                f"Hi {user.full_name},\n\n"
                f"Please verify your email address ({email}) by clicking the link below:\n\n"
                f"{verify_url}\n\n"
                f"This link expires in 24 hours.\n\n"
                f"If you did not create an account, please ignore this email.\n\n"
                f"— EduSphere Team"
            ),
        )

        AuditLog.objects.create(
            school=user.school,
            user=user,
            action="send_verification_email",
            resource_type="user",
            resource_id=str(user.id),
            ip_address=_get_client_ip(request),
        )

        return Response(
            {
                "detail": "Verification email sent. Check your inbox (and spam folder).",
            }
        )


class ConfirmEmailVerificationView(APIView):
    """
    Verify a token and mark the user's email as verified.
    Accepts both authenticated requests (verify own email) and
    unauthenticated requests (clicking link in email).
    """

    permission_classes = [AllowAny]
    throttle_classes = [AuthPasswordResetConfirmThrottle]

    def post(self, request):
        from .models import EmailVerificationToken
        from .serializers import ConfirmEmailVerificationSerializer

        serializer = ConfirmEmailVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token_str = serializer.validated_data["token"]

        try:
            verification = EmailVerificationToken.objects.select_related("user").get(token=token_str, used=False)
        except EmailVerificationToken.DoesNotExist:
            return Response(
                {"detail": "Invalid or already used verification link."},
                status=400,
            )

        if verification.is_expired:
            return Response(
                {"detail": "This verification link has expired. Request a new one."},
                status=400,
            )

        user = verification.user

        # Confirm the user is the authenticated user (if logged in)
        if request.user.is_authenticated and request.user.id != user.id:
            return Response(
                {"detail": "This verification link belongs to another user."},
                status=403,
            )

        user.email_verified = True
        user.email = verification.email  # Update email in case it was changed
        user.save(update_fields=["email_verified", "email"])

        verification.used = True
        verification.save(update_fields=["used"])

        AuditLog.objects.create(
            school=user.school,
            user=user,
            action="confirm_email_verification",
            resource_type="user",
            resource_id=str(user.id),
            ip_address=_get_client_ip(request),
        )

        return Response(
            {
                "detail": "Email verified successfully.",
                "email_verified": True,
            }
        )


class RegenerateBackupCodesView(APIView):
    """
    Invalidate existing backup codes and generate a fresh set.
    Requires the user's password for security.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        current_password = request.data.get("password", "")
        if not user.check_password(current_password):
            return Response({"detail": "Invalid password."}, status=400)

        if not user.two_factor_enabled:
            return Response({"detail": "2FA is not enabled."}, status=400)

        backup_codes = _generate_backup_codes(user)

        AuditLog.objects.create(
            school=user.school,
            user=user,
            action="regenerate_backup_codes",
            resource_type="user",
            resource_id=str(user.id),
            ip_address=_get_client_ip(request),
        )

        return Response(
            {
                "backup_codes": backup_codes,
                "detail": "New backup codes generated. Previous codes are no longer valid.",
            }
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    """Lightweight endpoint to check token validity and fetch own user data."""
    from core.plan_features import plan_features_for_tier

    data = UserProfileSerializer(request.user).data
    school = getattr(request.user, "school", None)
    tier = getattr(school, "subscription_tier", "basic") if school else "basic"
    data["plan_features"] = plan_features_for_tier(tier)
    return Response(data)


class PlanView(APIView):
    """Plan & billing overview for the authenticated user's school.

    Returns the current tier, the full feature matrix (every gated
    capability with per-tier availability), and an admin-only change-tier
    hint. Available to every school member — the matrix doubles as the
    in-app upgrade advertisement.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        from core.plan_features import PREMIUM_FEATURES, STANDARD_FEATURES, TIER_PRICING, plan_features_for_tier

        school = getattr(request.user, "school", None)
        tier = getattr(school, "subscription_tier", "basic") if school else "basic"

        matrix = [
            {
                "key": feature.key,
                "label": feature.label,
                "basic": False,
                "standard": feature.key in STANDARD_FEATURES,
                "premium": True,
            }
            for feature in PREMIUM_FEATURES
        ]

        return Response(
            {
                "plan": tier,
                "is_premium": tier == "premium",
                "school_name": school.name if school else None,
                "features": plan_features_for_tier(tier)["features"],
                "matrix": matrix,
                "can_manage": request.user.role in ("school_admin", "super_admin"),
                "pricing": TIER_PRICING,
            }
        )


class PlanChangeTierView(APIView):
    """Change the authenticated admin's school subscription tier.

    Stand-in for real billing: school/super admins may move their school
    between basic, standard, and premium directly (demo environments use
    this as the upgrade CTA target). Other roles get 403.
    """

    permission_classes = [IsAuthenticated, IsSchoolAdmin]

    def post(self, request):
        from core.plan_features import plan_features_for_tier

        school = request.user.school
        tier = str(request.data.get("tier", "")).strip().lower()
        if tier not in ("basic", "standard", "premium"):
            return Response(
                {"detail": "tier must be one of: basic, standard, premium."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if school.subscription_tier == tier:
            return Response(
                {"detail": f"School is already on the {tier} plan."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        previous = school.subscription_tier
        school.subscription_tier = tier
        school.save(update_fields=["subscription_tier", "updated_at"])

        AuditLog.objects.create(
            school=school,
            user=request.user,
            action="plan_tier_change",
            resource_type="school",
            resource_id=str(school.id),
            ip_address=request.META.get("REMOTE_ADDR"),
        )

        return Response(
            {
                "detail": f"Plan changed from {previous} to {tier}.",
                "plan": tier,
                "plan_features": plan_features_for_tier(tier),
            }
        )


# ═══════════════════════════════════════════════════════════════════════════════
# Super Admin — Platform Management
# ═══════════════════════════════════════════════════════════════════════════════


class PlatformDashboardView(APIView):
    """
    Cross-school analytics for the super admin platform dashboard.
    Returns aggregate counts, revenue, and recent/top schools.
    """

    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def get(self, request):
        from django.core.cache import cache
        from django.db.models import Count, Q, Sum
        from services.fees.models import Payment

        cache_key = "platform_dashboard_stats"

        # Try cache first; returns None on miss or if Redis is unavailable
        cached = cache.get(cache_key)
        if cached is not None:
            return Response(cached)

        logger.debug("Platform dashboard stats cache miss")

        schools = School.objects.all()
        total_schools = schools.count()
        active_schools = schools.filter(is_active=True).count()

        # User counts
        total_users = User.objects.count()
        total_students = User.objects.filter(role="student").count()
        total_teachers = User.objects.filter(role="teacher").count()

        # Revenue across all schools
        revenue_result = Payment.objects.filter(status="successful").aggregate(total=Sum("amount"))
        total_revenue = revenue_result["total"] or 0

        # Schools by subscription tier
        schools_by_tier = dict(
            schools.values("subscription_tier").annotate(count=Count("id")).values_list("subscription_tier", "count")
        )

        # Most recent 5 schools (pass raw queryset — let serializer handle it)
        recent_schools = schools.order_by("-created_at")[:5]

        # Top schools by revenue
        top_schools_data = (
            School.objects.annotate(
                school_revenue=Sum(
                    "users__student_profile__invoices__payments__amount",
                    filter=Q(users__student_profile__invoices__payments__status="successful"),
                )
            )
            .values("id", "name", "code", "school_revenue")
            .order_by("-school_revenue")[:5]
        )

        data = {
            "total_schools": total_schools,
            "active_schools": active_schools,
            "total_users": total_users,
            "total_students": total_students,
            "total_teachers": total_teachers,
            "total_revenue": total_revenue,
            "schools_by_tier": schools_by_tier,
            "recent_schools": recent_schools,
            "top_schools": [
                {
                    "id": str(s["id"]),
                    "name": s["name"],
                    "code": s["code"],
                    "revenue": float(s["school_revenue"] or 0),
                }
                for s in top_schools_data
            ],
        }

        serializer = PlatformDashboardSerializer(instance=data)
        result = serializer.data
        cache.set(cache_key, result, 300)  # 5 minute TTL
        return Response(result)


# ═══════════════════════════════════════════════════════════════════════════════
# Auth Module ViewSets
# ═══════════════════════════════════════════════════════════════════════════════


class PlatformRevenueView(APIView):
    """Revenue & Plans — per-school billing overview for the platform console.

    For every school: subscription tier, per-tier pricing × its student count
    (the platform's MRR), and successful revenue collected all-time. Super
    admin only.
    """

    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def get(self, request):
        from core.plan_features import TIER_PRICING
        from django.db.models import Count, Q, Sum

        schools = School.objects.annotate(
            student_count=Count("users", filter=Q(users__role="student"), distinct=True),
            revenue=Sum(
                "users__student_profile__invoices__payments__amount",
                filter=Q(users__student_profile__invoices__payments__status="successful"),
            ),
        ).values("id", "name", "code", "subscription_tier", "is_active", "student_count", "revenue")

        tiers = {}
        total_mrr = 0
        rows = []
        for s in schools:
            pricing = TIER_PRICING.get(s["subscription_tier"], TIER_PRICING["basic"])
            mrr = (pricing["per_student_month"] or 0) * (s["student_count"] or 0)
            total_mrr += mrr
            tiers[s["subscription_tier"]] = tiers.get(s["subscription_tier"], 0) + 1
            rows.append(
                {
                    **s,
                    "revenue": float(s["revenue"] or 0),
                    "mrr": mrr,
                    "arr": mrr * 10,
                }
            )

        rows.sort(key=lambda r: -r["mrr"])
        return Response(
            {
                "total_mrr": total_mrr,
                "total_arr": total_mrr * 10,
                "schools_by_tier": tiers,
                "schools": rows,
            }
        )


class SchoolViewSet(viewsets.ModelViewSet):
    """
    School records. Super admins manage all schools (list/create/toggle/add
    admins); school members can only read/update their own school.
    """

    serializer_class = SchoolSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["is_active", "subscription_tier"]
    search_fields = ["name", "code", "subdomain", "email"]
    ordering_fields = ["name", "created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.role == UserRole.SUPER_ADMIN:
            return School.objects.all()
        if user.is_authenticated and user.school_id:
            return School.objects.filter(id=user.school_id)
        return School.objects.none()

    def get_permissions(self):
        if self.action in ["create", "destroy", "toggle_active", "admins", "add_admin"]:
            # platform management is super-admin only
            return [IsAuthenticated(), IsSuperAdmin()]
        # list/retrieve/update: super admins (platform) and school members
        # (their own school only — enforced by get_queryset)
        return [IsAuthenticated()]

    @action(detail=True, methods=["post"])
    def toggle_active(self, request, pk=None):
        """Activate or deactivate a school (super admin)."""
        school = self.get_object()
        school.is_active = not school.is_active
        school.save(update_fields=["is_active"])
        return Response({"id": school.id, "is_active": school.is_active})

    @action(detail=True, methods=["get"])
    def admins(self, request, pk=None):
        """List school admin users for a given school."""
        school = self.get_object()
        admins = User.objects.filter(school=school, role=UserRole.SCHOOL_ADMIN)
        page = self.paginate_queryset(admins)
        if page is not None:
            serializer = SchoolAdminSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = SchoolAdminSerializer(admins, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def add_admin(self, request, pk=None):
        """Create a school admin user for a given school (super admin)."""
        school = self.get_object()
        serializer = SchoolAdminSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save(school=school, email_verified=True)
        return Response(SchoolAdminSerializer(user).data, status=status.HTTP_201_CREATED)


class UserSessionViewSet(viewsets.ModelViewSet):
    serializer_class = UserSessionSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return UserSession.objects.filter(user__school=self.request.user.school).select_related("user")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        user = serializer.validated_data.get("user")
        if user is not None and user.school_id != self.request.user.school_id:
            raise PermissionDenied("User does not belong to your school.")
        serializer.save()


class PasswordResetTokenViewSet(viewsets.ModelViewSet):
    serializer_class = PasswordResetTokenSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return PasswordResetToken.objects.filter(user__school=self.request.user.school).select_related("user")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        user = serializer.validated_data.get("user")
        if user is not None and user.school_id != self.request.user.school_id:
            raise PermissionDenied("User does not belong to your school.")
        serializer.save()


class EmailVerificationTokenViewSet(viewsets.ModelViewSet):
    serializer_class = EmailVerificationTokenSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return EmailVerificationToken.objects.filter(user__school=self.request.user.school).select_related("user")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        user = serializer.validated_data.get("user")
        if user is not None and user.school_id != self.request.user.school_id:
            raise PermissionDenied("User does not belong to your school.")
        serializer.save()


class TwoFactorBackupCodeViewSet(viewsets.ModelViewSet):
    serializer_class = TwoFactorBackupCodeSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return TwoFactorBackupCode.objects.filter(user__school=self.request.user.school).select_related("user")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        user = serializer.validated_data.get("user")
        if user is not None and user.school_id != self.request.user.school_id:
            raise PermissionDenied("User does not belong to your school.")
        serializer.save()


class AuditLogViewSet(viewsets.ModelViewSet):
    serializer_class = AuditLogSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = [
        "action",
        "resource_type",
        "resource_id",
        "user__email",
        "user__first_name",
        "user__last_name",
        "ip_address",
    ]
    filterset_fields = ["action", "resource_type", "user"]

    def get_queryset(self):
        if self.request.user.role == "super_admin":
            return AuditLog.objects.all().select_related("user", "school")
        return AuditLog.objects.filter(school=self.request.user.school).select_related("user")

    def get_permissions(self):
        # getattr guard: schema generation introspects this view without an
        # authenticated user, so ``request.user.role`` would raise.
        if getattr(self.request.user, "role", None) == "super_admin":
            return [IsAuthenticated()]
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class LoginHistoryViewSet(viewsets.ModelViewSet):
    serializer_class = LoginHistorySerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return LoginHistory.objects.filter(user__school=self.request.user.school).select_related("user")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        user = serializer.validated_data.get("user")
        if user is not None and user.school_id != self.request.user.school_id:
            raise PermissionDenied("User does not belong to your school.")
        serializer.save()


class APIKeyViewSet(viewsets.ModelViewSet):
    serializer_class = APIKeySerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name", "description"]
    filterset_fields = ["status"]

    def get_queryset(self):
        return APIKey.objects.filter(school=self.request.user.school).select_related("user")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        raw = secrets.token_urlsafe(24)
        serializer.save(
            school=self.request.user.school,
            user=self.request.user,
            key_prefix=raw[:8].upper(),
            key_hash=hashlib.sha256(raw.encode()).hexdigest(),
        )


class DeviceManagementViewSet(viewsets.ModelViewSet):
    serializer_class = DeviceManagementSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return DeviceManagement.objects.filter(user__school=self.request.user.school).select_related("user")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        user = serializer.validated_data.get("user")
        if user is not None and user.school_id != self.request.user.school_id:
            raise PermissionDenied("User does not belong to your school.")
        serializer.save()


class PasswordPolicyViewSet(viewsets.ModelViewSet):
    serializer_class = PasswordPolicySerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return PasswordPolicy.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class IPWhitelistViewSet(viewsets.ModelViewSet):
    serializer_class = IPWhitelistSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return IPWhitelist.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class OAuthProviderViewSet(viewsets.ModelViewSet):
    serializer_class = OAuthProviderSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return OAuthProvider.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class UserActivityViewSet(viewsets.ModelViewSet):
    serializer_class = UserActivitySerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return UserActivity.objects.filter(user__school=self.request.user.school).select_related("user")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        user = serializer.validated_data.get("user")
        if user is not None and user.school_id != self.request.user.school_id:
            raise PermissionDenied("User does not belong to your school.")
        serializer.save()


class SessionPolicyViewSet(viewsets.ModelViewSet):
    serializer_class = SessionPolicySerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return SessionPolicy.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class RoleViewSet(viewsets.ModelViewSet):
    serializer_class = RoleSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return Role.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class PermissionViewSet(viewsets.ModelViewSet):
    """
    Global permission catalog — shared across schools, not tenant-scoped.
    School members read it to build role grants; only super admins mutate it.
    """

    serializer_class = PermissionSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "codename", "module"]
    filterset_fields = ["permission_type", "module", "is_active"]
    ordering_fields = ["module", "name", "permission_type"]
    ordering = ["module", "name"]

    def get_queryset(self):
        return Permission.objects.all()

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSuperAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]


class RolePermissionViewSet(viewsets.ModelViewSet):
    """
    Grant catalog permissions to a school's roles. Model has no `school` FK,
    so all rows are scoped through `role__school`.
    """

    serializer_class = RolePermissionSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["role__name", "permission__name", "permission__codename"]
    filterset_fields = ["role", "permission", "granted"]

    def get_queryset(self):
        return RolePermission.objects.filter(role__school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        role = serializer.validated_data.get("role")
        if role is None or role.school_id != self.request.user.school_id:
            raise PermissionDenied("Role does not belong to your school.")
        serializer.save(granted_by=self.request.user)

    def perform_update(self, serializer):
        role = serializer.validated_data.get("role")
        if role is not None and role.school_id != self.request.user.school_id:
            raise PermissionDenied("Role does not belong to your school.")
        serializer.save()


class UserRoleViewSet(viewsets.ModelViewSet):
    """
    Assign a school role to a user of the same school. Model has no `school`
    FK, so rows are scoped through `user__school`.
    """

    serializer_class = UserRoleSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["user__email", "user__first_name", "user__last_name", "role__name"]
    filterset_fields = ["user", "role", "is_active"]

    def get_queryset(self):
        return UserRoleAssignment.objects.filter(user__school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        user = serializer.validated_data.get("user")
        role = serializer.validated_data.get("role")
        if user is None or user.school_id != self.request.user.school_id:
            raise PermissionDenied("User does not belong to your school.")
        if role is None or role.school_id != self.request.user.school_id:
            raise PermissionDenied("Role does not belong to your school.")
        serializer.save(assigned_by=self.request.user)

    def perform_update(self, serializer):
        user = serializer.validated_data.get("user")
        role = serializer.validated_data.get("role")
        if user is not None and user.school_id != self.request.user.school_id:
            raise PermissionDenied("User does not belong to your school.")
        if role is not None and role.school_id != self.request.user.school_id:
            raise PermissionDenied("Role does not belong to your school.")
        serializer.save()


class UserDirectoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only directory of the requesting user's school (role assignment
    pickers). Searchable by name/email; never exposes credentials.
    """

    serializer_class = UserDirectorySerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, IsSchoolAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["email", "first_name", "last_name"]
    filterset_fields = ["role", "is_active"]

    def get_queryset(self):
        return User.objects.filter(school=self.request.user.school).order_by("first_name", "last_name")


class SecurityPolicyViewSet(viewsets.ModelViewSet):
    serializer_class = SecurityPolicySerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return SecurityPolicy.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class LoginAttemptViewSet(viewsets.ModelViewSet):
    serializer_class = LoginAttemptSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return LoginAttempt.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class SessionTokenViewSet(viewsets.ModelViewSet):
    serializer_class = SessionTokenSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return SessionToken.objects.filter(user__school=self.request.user.school).select_related("user")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        user = serializer.validated_data.get("user")
        if user is not None and user.school_id != self.request.user.school_id:
            raise PermissionDenied("User does not belong to your school.")
        serializer.save()


class MFAMethodViewSet(viewsets.ModelViewSet):
    serializer_class = MFAMethodSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return MFAMethod.objects.filter(user__school=self.request.user.school).select_related("user")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        user = serializer.validated_data.get("user")
        if user is not None and user.school_id != self.request.user.school_id:
            raise PermissionDenied("User does not belong to your school.")
        serializer.save()


class MFAVerificationViewSet(viewsets.ModelViewSet):
    serializer_class = MFAVerificationSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return MFAVerification.objects.filter(mfa_method__user__school=self.request.user.school).select_related(
            "mfa_method__user"
        )

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        user = serializer.validated_data.get("user")
        if user is not None and user.school_id != self.request.user.school_id:
            raise PermissionDenied("User does not belong to your school.")
        serializer.save()


class OAuthTokenViewSet(viewsets.ModelViewSet):
    serializer_class = OAuthTokenSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return OAuthToken.objects.filter(user__school=self.request.user.school).select_related("user", "provider")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        user = serializer.validated_data.get("user")
        if user is not None and user.school_id != self.request.user.school_id:
            raise PermissionDenied("User does not belong to your school.")
        serializer.save()


class UserSessionHistoryViewSet(viewsets.ModelViewSet):
    serializer_class = UserSessionHistorySerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return UserSessionHistory.objects.filter(user__school=self.request.user.school).select_related("user")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        api_key = serializer.validated_data.get("api_key")
        if api_key is not None and api_key.school_id != self.request.user.school_id:
            raise PermissionDenied("API key does not belong to your school.")
        serializer.save()


class APIUsageLogViewSet(viewsets.ModelViewSet):
    serializer_class = APIUsageLogSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return APIUsageLog.objects.filter(api_key__school=self.request.user.school).select_related("api_key")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        api_key = serializer.validated_data.get("api_key")
        if api_key is not None and api_key.school_id != self.request.user.school_id:
            raise PermissionDenied("API key does not belong to your school.")
        serializer.save()


class ComplianceRecordViewSet(viewsets.ModelViewSet):
    serializer_class = ComplianceRecordSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return ComplianceRecord.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class PasswordHistoryViewSet(viewsets.ModelViewSet):
    serializer_class = PasswordHistorySerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return PasswordHistory.objects.filter(user__school=self.request.user.school).select_related("user")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        user = serializer.validated_data.get("user")
        if user is not None and user.school_id != self.request.user.school_id:
            raise PermissionDenied("User does not belong to your school.")
        serializer.save()


class UserTrustScoreViewSet(viewsets.ModelViewSet):
    serializer_class = UserTrustScoreSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return UserTrustScore.objects.filter(user__school=self.request.user.school).select_related("user")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        user = serializer.validated_data.get("user")
        if user is not None and user.school_id != self.request.user.school_id:
            raise PermissionDenied("User does not belong to your school.")
        serializer.save()


class SecurityNotificationPreferenceViewSet(viewsets.ModelViewSet):
    serializer_class = SecurityNotificationPreferenceSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return SecurityNotificationPreference.objects.filter(user__school=self.request.user.school).select_related(
            "user"
        )

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        user = serializer.validated_data.get("user")
        if user is not None and user.school_id != self.request.user.school_id:
            raise PermissionDenied("User does not belong to your school.")
        serializer.save()


class DataExportRequestViewSet(viewsets.ModelViewSet):
    serializer_class = DataExportRequestSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return DataExportRequest.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class DataDeletionRequestViewSet(viewsets.ModelViewSet):
    serializer_class = DataDeletionRequestSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return DataDeletionRequest.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class AuthWebhookViewSet(viewsets.ModelViewSet):
    serializer_class = AuthWebhookSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return AuthWebhook.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class WebhookDeliveryViewSet(viewsets.ModelViewSet):
    serializer_class = WebhookDeliverySerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return WebhookDelivery.objects.filter(webhook__school=self.request.user.school).select_related("webhook")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        webhook = serializer.validated_data.get("webhook")
        if webhook is not None and webhook.school_id != self.request.user.school_id:
            raise PermissionDenied("Webhook does not belong to your school.")
        serializer.save()


class SSOConfigurationViewSet(viewsets.ModelViewSet):
    serializer_class = SSOConfigurationSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return SSOConfiguration.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class DomainVerificationViewSet(viewsets.ModelViewSet):
    serializer_class = DomainVerificationSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return DomainVerification.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class IPGeolocationCacheViewSet(viewsets.ModelViewSet):
    serializer_class = IPGeolocationCacheSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return IPGeolocationCache.objects.all()

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()


class ConsentRecordViewSet(viewsets.ModelViewSet):
    serializer_class = ConsentRecordSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return ConsentRecord.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class SchoolFeatureFlagViewSet(viewsets.ModelViewSet):
    serializer_class = SchoolFeatureFlagSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return SchoolFeatureFlag.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class AuditReportScheduleViewSet(viewsets.ModelViewSet):
    serializer_class = AuditReportScheduleSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return AuditReportSchedule.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)
