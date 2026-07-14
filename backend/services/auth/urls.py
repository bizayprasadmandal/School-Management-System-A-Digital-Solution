from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = "auth_v1"

router = DefaultRouter()
router.register("audit-logs", views.AuditLogViewSet, basename="audit-log")

urlpatterns = [
    path("", include(router.urls)),
    path("login/",                   views.LoginView.as_view(),                name="login"),
    path("logout/",                  views.LogoutView.as_view(),               name="logout"),
    path("token/refresh/",           TokenRefreshView.as_view(),               name="token_refresh"),
    path("me/",                      views.me,                                 name="me"),
    path("profile/",                 views.ProfileView.as_view(),              name="profile"),
    path("change-password/",         views.ChangePasswordView.as_view(),       name="change_password"),
    path("password-reset/",          views.RequestPasswordResetView.as_view(), name="password_reset"),
    path("password-reset/confirm/",  views.ConfirmPasswordResetView.as_view(), name="password_reset_confirm"),

    # 2FA
    path("setup-2fa/",               views.Setup2FAView.as_view(),             name="setup_2fa"),
    path("verify-2fa/",              views.Verify2FAView.as_view(),            name="verify_2fa"),
    path("disable-2fa/",             views.Disable2FAView.as_view(),           name="disable_2fa"),
    path("verify-2fa-login/",        views.Verify2FALoginView.as_view(),       name="verify_2fa_login"),

    # Email Verification
    path("send-verification/",       views.SendEmailVerificationView.as_view(),    name="send_verification"),
    path("verify-email/",            views.ConfirmEmailVerificationView.as_view(), name="confirm_verification"),

    # 2FA Backup Codes
    path("regenerate-backup-codes/", views.RegenerateBackupCodesView.as_view(),    name="regenerate_backup_codes"),
]
