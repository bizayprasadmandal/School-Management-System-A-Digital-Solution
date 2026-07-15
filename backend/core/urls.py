"""
School Management System — Root URL Configuration
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from api.graphql.view import JWTAuthenticatedGraphQLView
from django.views.decorators.csrf import csrf_exempt

API_V1 = "api/v1/"
API_V2 = "api/v2/"

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),

    # Health check
    path("health/", include("core.health.urls")),

    # ── REST API v1 ──────────────────────────────────────────────────────────
    path(API_V1 + "auth/", include("services.auth.urls", namespace="auth_v1")),
    path(API_V1 + "students/", include("services.students.urls", namespace="students_v1")),
    path(API_V1 + "academics/", include("services.academics.urls", namespace="academics_v1")),
    path(API_V1 + "attendance/", include("services.attendance.urls", namespace="attendance_v1")),
    path(API_V1 + "gradebook/", include("services.gradebook.urls", namespace="gradebook_v1")),
    path(API_V1 + "timetable/", include("services.timetable.urls", namespace="timetable_v1")),
    path(API_V1 + "communication/", include("services.communication.urls", namespace="communication_v1")),
    path(API_V1 + "reporting/", include("services.reporting.urls", namespace="reporting_v1")),
    path(API_V1 + "fees/", include("services.fees.urls", namespace="fees_v1")),
    path(API_V1 + "behavior/", include("services.behavior.urls", namespace="behavior_v1")),
    path(API_V1 + "library/", include("services.library.urls", namespace="library_v1")),
    path(API_V1 + "conferences/", include("services.conferences.urls", namespace="conferences_v1")),
    path(API_V1 + "hr/", include("services.hr.urls", namespace="hr_v1")),
    path(API_V1 + "transport/", include("services.transportation.urls", namespace="transport_v1")),

    # ── GraphQL ──────────────────────────────────────────────────────────────
    path("graphql/", csrf_exempt(JWTAuthenticatedGraphQLView.as_view(graphiql=settings.DEBUG))),

    # ── API Docs ─────────────────────────────────────────────────────────────
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),

    # Metrics
    path("", include("django_prometheus.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
