"""Inspect failing viewsets: model name, school FK path, current get_queryset."""

import os
import sys

sys.path.insert(0, "/app")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.base")

import django

django.setup()

from services import conferences, fees, reporting  # noqa: E402

FAILURES = {
    "reporting": [
        "CustomReportExecution",
        "DashboardConfiguration",
        "DashboardWidgetPlacement",
        "KPIValue",
        "ReportAccessControl",
        "ReportAccessLog",
        "ReportBookmark",
        "ReportComment",
        "ReportEmailDelivery",
        "ReportFavorite",
        "ReportFolderItem",
        "ReportScheduleDelivery",
        "ReportSubscription",
        "ReportTemplateParameter",
        "ReportVersion",
    ],
    "conferences": [
        "ConferenceAccessibilityRequirement",
        "ConferenceApproval",
        "ConferenceCalendarSync",
        "ConferenceConferenceType",
        "ConferenceFollowUp",
        "ConferenceNoShow",
        "ConferenceResource",
        "ConferenceRoomBooking",
        "ConferenceSurveyResponse",
        "ConferenceTemplateSection",
        "RecurringConferenceParticipant",
    ],
    "fees": ["BudgetLineItem", "PaymentGatewayConfig"],
}

for mod_name, models in FAILURES.items():
    mod = {"reporting": reporting, "conferences": conferences, "fees": fees}[mod_name]
    print(f"== {mod_name} ==")
    for name in models:
        try:
            m = getattr(mod.models, name)
        except AttributeError:
            print(f"  {name}: NOT FOUND")
            continue
        fields = {f.name: f for f in m._meta.get_fields()}
        rels = [f for f in fields.values() if f.is_relation and not f.auto_created]
        rel_names = []
        for f in rels:
            target = f.related_model.__name__
            rel_names.append(f"{f.name}->{target}")
        print(f"  {name}: {rel_names}")
