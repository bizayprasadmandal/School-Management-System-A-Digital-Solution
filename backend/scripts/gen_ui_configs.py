"""Generate TS EntityConfig arrays from route_serializer_map.json + cluster_fields.json + cluster_choices.json."""

import json
import re
import sys as _sys

fields = json.load(
    open("scripts/" + (_sys.argv[1] if len(_sys.argv) > 1 else "cluster") + "_fields.json", encoding="utf-8")
)
choices = json.load(
    open("scripts/" + (_sys.argv[1] if len(_sys.argv) > 1 else "cluster") + "_choices.json", encoding="utf-8")
)
route_map = json.load(
    open("scripts/" + (_sys.argv[1] if len(_sys.argv) > 1 else "cluster") + "_map.json", encoding="utf-8")
)

SKIP_FIELDS = {"id", "created_at", "updated_at", "school", "user"}

DATE_FIELDS = {
    "date",
    "date_from",
    "date_to",
    "snapshot_date",
    "submission_date",
    "due_date",
    "scheduled_at",
    "starts_at",
    "ends_at",
    "start_date",
    "end_date",
    "last_seen",
    "last_generated",
    "next_generation",
    "expires_at",
    "accessed_at",
    "sent_at",
    "delivered_at",
    "requested_at",
    "completed_at",
    "started_at",
    "triggered_at",
    "generated_at",
    "last_notified_at",
    "last_triggered_at",
    "last_synced_at",
    "last_hit_at",
    "trusted_at",
    "blocked_at",
    "last_login",
    "date",
}
BOOL_FIELDS = {
    "is_active",
    "is_public",
    "is_default",
    "is_visible",
    "is_shared",
    "is_read",
    "is_current",
    "is_required",
    "password_protected",
    "email_delivery",
    "target_met",
    "stripe_enabled",
    "khalti_enabled",
    "esewa_enabled",
}
NUMBER_FIELDS = {
    "amount",
    "total_amount",
    "paid_amount",
    "outstanding_amount",
    "target_value",
    "min_value",
    "max_value",
    "warning_threshold",
    "critical_threshold",
    "threshold_value",
    "value",
    "percentage",
    "score",
    "average_score",
    "average_class_score",
    "attendance_rate",
    "enrollment_change",
    "performance_change",
    "attendance_change",
    "position",
    "sort_order",
    "width",
    "height",
    "record_count",
    "view_count",
    "trigger_count",
    "hit_count",
    "file_size_bytes",
    "version_number",
    "total_students",
    "total_staff",
    "total_reports_generated",
    "total_reports_viewed",
    "total_reports_exported",
    "active_users",
    "avg_generation_time",
    "avg_attendance",
    "avg_gpa",
    "pass_rate",
    "total_revenue",
    "total_expenses",
    "new_enrollments",
    "dropouts",
    "recipient_count",
    "duration_seconds",
    "refresh_interval_seconds",
    "position_x",
    "position_y",
    "total_views",
}
TEXTAREA_FIELDS = {
    "description",
    "summary",
    "notes",
    "report_data",
    "data",
    "config",
    "data_sources",
    "default_filters",
    "available_filters",
    "columns",
    "default_sort",
    "group_by",
    "aggregations",
    "chart_config",
    "filters",
    "saved_filters",
    "custom_config",
    "comparison_data",
    "highlights",
    "by_type_breakdown",
    "top_reports",
    "filters_applied",
    "strengths",
    "areas_for_improvement",
    "data_source",
    "query",
    "sql_query",
    "fields",
    "config_snapshot",
    "parameters",
    "result_file",
    "error_message",
    "message",
    "recipients",
    "shared_with",
    "visible_to_roles",
    "options",
    "default_value",
    "subject",
}
TITLE_CANDIDATES = ("name", "title", "report_type", "subject", "label", "snapshot_type")

SUB_CANDIDATES = (
    "status",
    "report_type",
    "frequency",
    "format",
    "snapshot_type",
    "alert_type",
    "insight_type",
    "access_level",
    "share_type",
    "update_type",
    "param_type",
    "source_type",
    "item_type",
    "compliance_type",
    "trend_type",
    "progress_type",
    "delivery_method",
    "category",
    "priority",
    "chart_type",
    "widget_type",
    "data_type",
    "cache_key",
    "report_id",
    "version_number",
    "location_type",
    "device_type",
    "method_type",
)


def human(name):
    return re.sub(r"(?<!^)(?=[A-Z])", " ", name).replace("_", " ").title()


import sys

MODULES = sys.argv[1:] or ["reporting", "conferences", "auth", "fees"]

for mod in MODULES:
    print(f"// ===== {mod} =====")
    mod_choices = choices.get(mod, {})
    for route, ser in sorted(route_map.get(mod, {}).items()):
        if not route or not ser:
            continue
        flds = fields.get(mod, {}).get(ser)
        if not flds:
            print(f"// NO FIELDS for {route} ({ser})")
            continue
        mname = ser[: -len("Serializer")]
        title = next((f for f in TITLE_CANDIDATES if f in flds), None)
        if not title or title in SKIP_FIELDS:
            title = next((f for f in flds if f not in SKIP_FIELDS), None)
        subtitle = next(
            (f for f in SUB_CANDIDATES if f in flds and f not in SKIP_FIELDS and f != title),
            None,
        )
        field_specs = []
        for f in flds:
            if f in SKIP_FIELDS:
                continue
            spec = {"key": f, "label": human(f)}
            ch = mod_choices.get(mname, {}).get(f)
            if ch:
                spec["type"] = "select"
                spec["options"] = [[str(c), str(c).replace("_", " ").title()] for c in ch]
            elif f in BOOL_FIELDS:
                spec["type"] = "bool"
            elif f in NUMBER_FIELDS:
                spec["type"] = "number"
            elif f in TEXTAREA_FIELDS:
                spec["type"] = "textarea"
            elif f in DATE_FIELDS or f.endswith("_at") or f.endswith("_date"):
                spec["type"] = "date"
            field_specs.append(spec)
        print("  {")
        print(f'    key: "{route}",')
        print(f'    label: "{human(mname)}",')
        print(f'    endpoint: "{route}",')
        print(f'    titleField: "{title}",')
        if subtitle:
            print(f'    subtitleField: "{subtitle}",')
        print(f"    fields: {json.dumps(field_specs)},")
        print("  },")
    print()
