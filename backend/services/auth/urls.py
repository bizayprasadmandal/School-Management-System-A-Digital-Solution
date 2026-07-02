from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = "auth_v1"

urlpatterns = [
    path("login/",                   views.LoginView.as_view(),                name="login"),
    path("logout/",                  views.LogoutView.as_view(),               name="logout"),
    path("token/refresh/",           TokenRefreshView.as_view(),               name="token_refresh"),
    path("me/",                      views.me,                                 name="me"),
    path("profile/",                 views.ProfileView.as_view(),              name="profile"),
    path("change-password/",         views.ChangePasswordView.as_view(),       name="change_password"),
    path("password-reset/",          views.RequestPasswordResetView.as_view(), name="password_reset"),
    path("password-reset/confirm/",  views.ConfirmPasswordResetView.as_view(), name="password_reset_confirm"),
]
