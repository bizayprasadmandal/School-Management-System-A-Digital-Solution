"""
Auth Service — Login, profile, password management, token views
"""

import secrets
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.password_validation import validate_password
from rest_framework import status, generics, parsers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema

from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from core.pagination import StandardResultsSetPagination
from core.permissions import IsSchoolAdmin

from core.throttles import (
    AuthLoginAnonThrottle,
    AuthPasswordResetThrottle,
    AuthPasswordResetConfirmThrottle,
    AuthVerify2FALoginThrottle,
)

import hashlib
import logging
from django.db.models import Sum, Count, Q
from .models import User, PasswordResetToken, AuditLog, TwoFactorBackupCode, School
from .serializers import (
    CustomTokenObtainPairSerializer, UserProfileSerializer, AuditLogSerializer,
    SchoolSerializer, SchoolAdminSerializer, PlatformDashboardSerializer,
)
from services.communication.services import send_in_app_notification

logger = logging.getLogger(__name__)

BACKUP_CODE_COUNT = 8


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
        codes_to_create.append(
            TwoFactorBackupCode(user=user, hashed_code=hashed)
        )

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
        bc = TwoFactorBackupCode.objects.get(
            user=user, hashed_code=hashed, used=False
        )
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
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            user = User.objects.get(email=request.data.get("email", ""))

            # 2FA check — if enabled, require TOTP verification
            if user.two_factor_enabled and user.two_factor_secret:
                return Response({
                    "requires_2fa": True,
                    "user_id": str(user.id),
                    "backup_codes_remaining": user.backup_codes.filter(used=False).count(),
                    "detail": "2FA is enabled. Please provide your TOTP code via /auth/verify-2fa/",
                }, status=200)

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
            school=user.school, user=user,
            action="profile_update", resource_type="user", resource_id=str(user.id),
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
            return Response({
                "avatar": user.avatar.url if user.avatar else None,
                "detail": "Avatar updated successfully.",
            })
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
            school=user.school, user=user,
            action="password_change", resource_type="user", resource_id=str(user.id),
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
                token=token_str,
                expires_at=timezone.now() + timedelta(hours=2),
            )
            # Send email async
            from services.communication.tasks import send_email_notification
            from django.conf import settings
            frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:3000")
            reset_url = request.data.get("reset_url", f"{frontend_url}/reset-password/{token_str}")
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
                token=token_str, used=False
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

        return Response({
            "secret": secret,
            "provisioning_uri": provisioning_uri,
            "backup_codes": backup_codes,
            "detail": "Scan the QR code with your authenticator app, then call /auth/verify-2fa/ to enable. Save your backup codes in a safe place.",
        })


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
                return Response({
                    "detail": "2FA enabled successfully.",
                    "backup_codes": backup_codes,
                })

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

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
            },
        })

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
            return Response({
                "detail": f"Too many failed backup code attempts. Try again in {remaining} seconds.",
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)

        if _check_backup_code(user, code):
            # Successful backup code use — reset lockout counter
            _reset_backup_code_lockout(user)
            return self._issue_jwt(user, request)

        # Failed backup code attempt — record it
        _record_failed_backup_code_attempt(user)

        attempts_left = BACKUP_CODE_LOCKOUT_LIMIT - user.backup_code_failed_attempts
        if attempts_left <= 0:
            return Response({
                "detail": "Too many failed backup code attempts. You are temporarily locked out. Try again in 30 minutes or use your authenticator app.",
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)

        return Response({
            "detail": f"Invalid verification code. {attempts_left} backup code attempt{'s' if attempts_left != 1 else ''} remaining before lockout."
        }, status=status.HTTP_400_BAD_REQUEST)


class SendEmailVerificationView(APIView):
    """
    Generate a verification token and send an email with the verification link.
    The user must be authenticated but have email_verified=False.
    """
    permission_classes = [IsAuthenticated]
    throttle_classes = [AuthPasswordResetThrottle]  # Reuse: 1 request per X time

    def post(self, request):
        from .serializers import SendEmailVerificationSerializer
        from .models import EmailVerificationToken
        from services.communication.tasks import send_email_notification

        serializer = SendEmailVerificationSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        user = request.user
        email = serializer.validated_data.get("email") or user.email

        # Invalidate any existing unused tokens for this user
        EmailVerificationToken.objects.filter(
            user=user, used=False, email=email
        ).update(used=True)

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
        base_url = request.data.get(
            "verification_base_url",
            frontend_url,
        )
        verify_url = f"{base_url}/verify-email/{token_str}"

        # Send email asynchronously
        send_email_notification.delay(
            user_id=str(user.id),
            subject="Verify Your Email Address — EduSphere SMS",
            body=(
                f"Hi {user.full_name},\n\n"
                f"Please verify your email address by clicking the link below:\n\n"
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

        return Response({
            "detail": "Verification email sent. Check your inbox (and spam folder).",
        })


class ConfirmEmailVerificationView(APIView):
    """
    Verify a token and mark the user's email as verified.
    Accepts both authenticated requests (verify own email) and
    unauthenticated requests (clicking link in email).
    """
    permission_classes = [AllowAny]
    throttle_classes = [AuthPasswordResetConfirmThrottle]

    def post(self, request):
        from .serializers import ConfirmEmailVerificationSerializer
        from .models import EmailVerificationToken

        serializer = ConfirmEmailVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token_str = serializer.validated_data["token"]

        try:
            verification = EmailVerificationToken.objects.select_related("user").get(
                token=token_str, used=False
            )
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

        return Response({
            "detail": "Email verified successfully.",
            "email_verified": True,
        })


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

        return Response({
            "backup_codes": backup_codes,
            "detail": "New backup codes generated. Previous codes are no longer valid.",
        })


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only audit log — admins can search, filter, and export.
    """
    serializer_class = AuditLogSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, IsSchoolAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["action", "resource_type", "user"]
    search_fields = ["action", "resource_type", "resource_id", "user__full_name", "user__email"]
    ordering = ["-timestamp"]
    ordering_fields = ["timestamp", "action"]

    def get_queryset(self):
        return AuditLog.objects.filter(
            school=self.request.user.school
        ).select_related("user")


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    """Lightweight endpoint to check token validity and fetch own user data."""
    return Response(UserProfileSerializer(request.user).data)


# ═══════════════════════════════════════════════════════════════════════════════
# Super Admin — Platform Management
# ═══════════════════════════════════════════════════════════════════════════════


class IsSuperAdmin(permissions.BasePermission):
    """Only super_admin can access platform-level endpoints."""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "super_admin"
        )


class SchoolViewSet(viewsets.ModelViewSet):
    """
    CRUD for schools — super admin only.
    Provides school-level stats (user/student/teacher counts, revenue).
    """
    serializer_class = SchoolSerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["is_active", "subscription_tier"]
    search_fields = ["name", "code", "subdomain", "email"]
    ordering_fields = ["name", "created_at", "user_count"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return School.objects.all().order_by("-created_at")

    @action(detail=True, methods=["post"])
    def toggle_active(self, request, pk=None):
        """Activate or deactivate a school."""
        school = self.get_object()
        school.is_active = not school.is_active
        school.save(update_fields=["is_active"])
        AuditLog.objects.create(
            user=request.user,
            action="toggle_school_active",
            resource_type="school",
            resource_id=str(school.id),
            changes={"is_active": school.is_active},
            ip_address=_get_client_ip(request),
        )
        return Response({"is_active": school.is_active})

    @action(detail=True, methods=["get"])
    def admins(self, request, pk=None):
        """List school admin users for a given school."""
        school = self.get_object()
        admins = User.objects.filter(school=school, role="school_admin")
        page = self.paginate_queryset(admins)
        if page is not None:
            serializer = SchoolAdminSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = SchoolAdminSerializer(admins, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def add_admin(self, request, pk=None):
        """Create a new school admin user for a given school."""
        school = self.get_object()
        serializer = SchoolAdminSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save(school=school, email_verified=True)
        AuditLog.objects.create(
            user=request.user,
            action="create_school_admin",
            resource_type="user",
            resource_id=str(user.id),
            changes={"school": school.name, "email": user.email},
            ip_address=_get_client_ip(request),
        )
        return Response(SchoolAdminSerializer(user).data, status=201)


class PlatformDashboardView(APIView):
    """
    Cross-school analytics for the super admin platform dashboard.
    Returns aggregate counts, revenue, and recent/top schools.
    """
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def get(self, request):
        from django.db.models import Count, Sum, Q
        from services.fees.models import Payment

        schools = School.objects.all()
        total_schools = schools.count()
        active_schools = schools.filter(is_active=True).count()

        # User counts
        total_users = User.objects.count()
        total_students = User.objects.filter(role="student").count()
        total_teachers = User.objects.filter(role="teacher").count()

        # Revenue across all schools
        revenue_result = Payment.objects.filter(
            status="completed"
        ).aggregate(total=Sum("amount"))
        total_revenue = revenue_result["total"] or 0

        # Schools by subscription tier
        schools_by_tier = dict(
            schools.values("subscription_tier").annotate(count=Count("id")).values_list("subscription_tier", "count")
        )

        # Most recent 5 schools
        recent_schools = schools.order_by("-created_at")[:5]

        # Top schools by revenue
        top_schools_data = (
            School.objects.annotate(
                school_revenue=Sum(
                    "users__student_enrollments__invoice__payment__amount",
                    filter=Q(users__student_enrollments__invoice__payment__status="completed"),
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
            "recent_schools": SchoolSerializer(recent_schools, many=True).data,
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

        serializer = PlatformDashboardSerializer(data)
        return Response(serializer.data)
