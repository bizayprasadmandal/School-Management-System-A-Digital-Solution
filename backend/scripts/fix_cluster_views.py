"""Fix school-scoping bugs in reporting/conferences/fees viewsets.

For each viewset whose model lacks a direct `school` FK, rewrite the
get_queryset filter to the correct parent path and strip invalid
`school=` kwargs from perform_create save() calls.
"""

import re

FIXES = {
    "services/reporting/views.py": {
        "CustomReportExecution": "report__school",
        "DashboardConfiguration": "user__school",
        "DashboardWidgetPlacement": "dashboard__school",
        "KPIValue": "kpi__school",
        "ReportAccessControl": "user__school",
        "ReportAccessLog": "report_history__school",
        "ReportBookmark": "user__school",
        "ReportComment": "report_history__school",
        "ReportEmailDelivery": "report_history__school",
        "ReportFavorite": "user__school",
        "ReportFolderItem": "folder__school",
        "ReportScheduleDelivery": "schedule__school",
        "ReportSubscription": "user__school",
        "ReportTemplateParameter": "template__school",
        "ReportVersion": "template__school",
    },
    "services/conferences/views.py": {
        "ConferenceAccessibilityRequirement": "booking__slot__school",
        "ConferenceApproval": "booking__slot__school",
        "ConferenceCalendarSync": "user__school",
        "ConferenceConferenceType": "conference_type__school",
        "ConferenceFollowUp": "booking__slot__school",
        "ConferenceNoShow": "booking__slot__school",
        "ConferenceResource": "booking__slot__school",
        "ConferenceRoomBooking": "location__school",
        "ConferenceSurveyResponse": "survey__school",
        "ConferenceTemplateSection": "template__school",
        "RecurringConferenceParticipant": "recurring_conference__school",
    },
    "services/fees/views.py": {
        "BudgetLineItem": "budget_plan__school",
    },
}


def viewset_span(src, name):
    start = src.index(f"class {name}ViewSet")
    nxt = src.find("\nclass ", start + 1)
    return start, (nxt if nxt != -1 else len(src))


for path, fixes in FIXES.items():
    src = open(path, encoding="utf-8").read()
    changed = 0
    for name, filter_path in fixes.items():
        start, end = viewset_span(src, name)
        block = src[start:end]
        new_block = block
        # fix filter path
        new_block = new_block.replace(
            f".filter(school=self.request.user.school)",
            f".filter({filter_path}=self.request.user.school)",
        )
        # remove invalid save(school=...) kwarg
        new_block = re.sub(
            r"serializer\.save\(school=self\.request\.user\.school\)",
            "serializer.save()",
            new_block,
        )
        if new_block != block:
            src = src[:start] + new_block + src[end:]
            changed += 1
        else:
            print(f"WARN no change: {name}")
    open(path, "w", encoding="utf-8", newline="").write(src)
    print(f"{path}: {changed} viewsets fixed")
