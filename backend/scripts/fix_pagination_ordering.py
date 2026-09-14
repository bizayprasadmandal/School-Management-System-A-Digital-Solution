"""Add explicit default ordering to viewsets flagged by
UnorderedObjectListWarning in the test suite.

Root cause: `.annotate()` on a queryset discards Meta.ordering for
pagination purposes (queryset.ordered becomes False). The flagged
viewsets either annotate their lists or the underlying model has no
Meta.ordering at all. Adding an explicit .order_by(...) in get_queryset
fixes pagination stability and silences the warning.

Per-model ordering (verified against live models):
  academics.LessonPlan            -> -created_at
  academics.TeacherAssignment     -> id
  academics.TeacherWorkloadConfig -> -updated_at
  behavior.Referral               -> -created_at
  fees.FeeCategory                -> name
  fees.FeeStructure               -> id
  fees.Scholarship                -> name
  gradebook.Assessment            -> -created_at
  gradebook.Exam                  -> -start_date
  gradebook.Grade                 -> -updated_at
  gradebook.ReportCard            -> id
  health_clinic.HealthRecord      -> -created_at
  timetable.TimetableSlot         -> day_of_week, period
  (models with Meta.ordering that lose it to .annotate())
  hr.Department                   -> name
  hr.TrainingProgram              -> -start_date
  inventory.Category              -> name
  sports.Sport                    -> name
  sports.Team                     -> sport, name
  transportation.Route            -> name
  admissions.EnrollmentIntake     -> -application_start
  cafeteria.MealMenu              -> -date, meal_type
"""

import re

# module -> [(viewset class, model, order_by tuple)]
FIXES = {
    "academics": [
        ("LessonPlanViewSet", "LessonPlan", ["-created_at"]),
        ("TeacherAssignmentViewSet", "TeacherAssignment", ["id"]),
        ("TeacherWorkloadConfigViewSet", "TeacherWorkloadConfig", ["-updated_at"]),
    ],
    "behavior": [("ReferralViewSet", "Referral", ["-created_at"])],
    "fees": [
        ("FeeCategoryViewSet", "FeeCategory", ["name"]),
        ("FeeStructureViewSet", "FeeStructure", ["id"]),
        ("ScholarshipViewSet", "Scholarship", ["name"]),
    ],
    "gradebook": [
        ("AssessmentViewSet", "Assessment", ["-created_at"]),
        ("ExamViewSet", "Exam", ["-start_date"]),
        ("GradeViewSet", "Grade", ["-updated_at"]),
        ("ReportCardViewSet", "ReportCard", ["id"]),
    ],
    "health_clinic": [("HealthRecordViewSet", "HealthRecord", ["-created_at"])],
    "timetable": [
        ("TimetableSlotViewSet", "TimetableSlot", ["day_of_week", "period"]),
    ],
    "hr": [
        ("DepartmentViewSet", "Department", ["name"]),
        ("TrainingProgramViewSet", "TrainingProgram", ["-start_date"]),
    ],
    "inventory": [("CategoryViewSet", "Category", ["name"])],
    "sports": [
        ("SportViewSet", "Sport", ["name"]),
        ("TeamViewSet", "Team", ["sport", "name"]),
    ],
    "transportation": [("RouteViewSet", "Route", ["name"])],
    "admissions": [("EnrollmentIntakeViewSet", "EnrollmentIntake", ["-application_start"])],
    "cafeteria": [("MealMenuViewSet", "MealMenu", ["-date", "meal_type"])],
}

total = 0
for mod, entries in FIXES.items():
    path = f"services/{mod}/views.py"
    src = open(path, encoding="utf-8").read().replace("\r\n", "\n")
    changed = 0
    for cls, model, order in entries:
        start = src.index(f"class {cls}(")
        nxt = src.find("\nclass ", start + 1)
        seg = src[start:nxt]
        # find the primary return of get_queryset for this model
        pat = re.compile(rf"(return {model}\.objects\.filter\((?:[^()]|\([^()]*\))*\))(?!\.order_by)")
        new_seg, n = pat.subn(rf"\1.order_by({', '.join(repr(o) for o in order)})", seg, count=1)
        if n:
            src = src[:start] + new_seg + src[nxt:]
            changed += 1
            print(f"{mod}: {cls} -> order_by({', '.join(order)})")
        else:
            print(f"{mod}: SKIP {cls} (pattern not found or already ordered)")
    if changed:
        open(path, "w", encoding="utf-8", newline="\n").write(src)
        total += changed

print(f"TOTAL: {total} viewsets ordered")
