"""
Auth Service — Login, profile, password management, token views
"""

import secrets
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.password_validation import validate_password
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema

from .models import User, PasswordResetToken, AuditLog
from .serializers import CustomTokenObtainPairSerializer, UserProfileSerializer


class LoginView(TokenObtainPairView):
    """
    Authenticate with email + password. Returns JWT access/refresh pair
    plus full user profile in the response body.
    """
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            # Log successful login
            user = User.objects.get(email=request.data.get("email", ""))
            user.last_login_ip = self._get_ip(request)
            user.save(update_fields=["last_login_ip"])
            AuditLog.objects.create(
                school=user.school,
                user=user,
                action="login",
                resource_type="user",
                resource_id=str(user.id),
                ip_address=self._get_ip(request),
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
            )
        return response

    def _get_ip(self, request):
        forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        return forwarded.split(",")[0].strip() if forwarded else request.META.get("REMOTE_ADDR")


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
        except Exception:
            return Response({"detail": "Invalid or expired token."}, status=400)


class ProfileView(generics.RetrieveUpdateAPIView):
    """Get/update the authenticated user's own profile."""
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


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
            send_email_notification.delay(
                user_id=str(user.id),
                subject="Password Reset Request",
                body=f"Click here to reset your password: {request.data.get('reset_url', 'https://app.edusphere.school')}/reset-password/{token_str}",
            )
        except User.DoesNotExist:
            pass

        return Response({"detail": "If an account with that email exists, a reset link has been sent."})


class ConfirmPasswordResetView(APIView):
    permission_classes = [AllowAny]

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


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    """Lightweight endpoint to check token validity and fetch own user data."""
    return Response(UserProfileSerializer(request.user).data)
