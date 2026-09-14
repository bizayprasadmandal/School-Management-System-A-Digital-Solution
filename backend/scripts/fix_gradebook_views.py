"""Fix gradebook module: register 6 orphaned viewsets with tenant scoping.

- ExamSchedule: scopes through exam__school.
- ExamType / GradingScale: direct school FK.
- GradingScaleEntry: through scale__school.
- GradeChangeLog: through student__school.
- RubricScore: through rubric_assessment__assessment__assignment__teacher__school.
Also adds perform_create for the direct-school models and makes school
read-only in their serializers.
"""

import re

VIEWS = "services/gradebook/views.py"
URLS = "services/gradebook/urls.py"
SER = "services/gradebook/serializers.py"

SCOPING = {
    "ExamScheduleViewSet": (
        "exam__school=self.request.user.school",
        '"exam__exam_type", "exam__academic_year", "subject", "classroom"',
    ),
    "ExamTypeViewSet": ("school=self.request.user.school", None),
    "GradeChangeLogViewSet": (
        "student__school=self.request.user.school",
        '"student__user", "exam_schedule", "changed_by"',
    ),
    "GradingScaleViewSet": ("school=self.request.user.school", None),
    "GradingScaleEntryViewSet": ("scale__school=self.request.user.school", '"scale"'),
    "RubricScoreViewSet": (
        "rubric_assessment__assessment__assignment__teacher__school=self.request.user.school",
        '"rubric_assessment__student__user", "criterion", "selected_level"',
    ),
}

PERFORM = {
    "ExamTypeViewSet": "serializer.save(school=self.request.user.school)",
    "GradingScaleViewSet": "serializer.save(school=self.request.user.school)",
}

RO = {
    "ExamTypeSerializer": "school",
    "GradingScaleSerializer": "school",
}

# 1. views.py: inject get_queryset + perform_create into the six orphan blocks
src = open(VIEWS, encoding="utf-8").read()
blocks = re.split(r"(?=^class \w+ViewSet)", src, flags=re.M)
out = [blocks[0]]
fixed = 0
for b in blocks[1:]:
    m = re.match(r"^class (\w+ViewSet)", b)
    name = m.group(1) if m else ""
    if name in SCOPING and "def get_queryset" not in b:
        filt, sel = SCOPING[name]
        sel_line = f".select_related({sel})" if sel else ""
        inject = (
            "\n    def get_queryset(self):\n"
            f"        return {name[:-len('ViewSet')]}.objects.filter({filt}){sel_line}\n"
        )
        b = re.sub(r"(serializer_class = \w+\n)", r"\1" + inject, b, count=1)
        fixed += 1
    if name in PERFORM and "perform_create" not in b:
        b = b.rstrip("\n") + f"\n\n    def perform_create(self, serializer):\n        {PERFORM[name]}\n"
    out.append(b)
src = "".join(out)
open(VIEWS, "w", encoding="utf-8", newline="\n").write(src)
print(f"viewsets scoped: {fixed}")

# 2. urls.py: register the six orphans
urlsrc = open(URLS, encoding="utf-8").read().replace("\r\n", "\n")
additions = (
    "# Expanded: exam scheduling & grading config\n"
    'router.register("exam-schedules", views.ExamScheduleViewSet, basename="exam-schedule")\n'
    'router.register("exam-types", views.ExamTypeViewSet, basename="exam-type")\n'
    'router.register("grading-scales", views.GradingScaleViewSet, basename="grading-scale")\n'
    'router.register("grading-scale-entries", views.GradingScaleEntryViewSet, basename="grading-scale-entry")\n'
    'router.register("grade-change-logs", views.GradeChangeLogViewSet, basename="grade-change-log")\n'
    'router.register("rubric-scores", views.RubricScoreViewSet, basename="rubric-score")\n'
)
if "exam-schedules" not in urlsrc:
    urlsrc = urlsrc.replace(
        'urlpatterns = [path("", include(router.urls))]',
        additions + '\nurlpatterns = [path("", include(router.urls))]',
    )
    open(URLS, "w", encoding="utf-8", newline="\n").write(urlsrc)
    print("urls: 6 routes registered")
else:
    print("urls: already registered")

# 3. serializers.py: make school read-only on direct-school models
ser = open(SER, encoding="utf-8").read()
for name, field in RO.items():
    pat = re.compile(
        r"(class " + name + r"\(serializers\.ModelSerializer\):.*?read_only_fields = \[[^\]]*)\]",
        re.S,
    )
    new_ser, n = pat.subn(r"\1, \"" + field + '"]', ser)
    if n:
        ser = new_ser
open(SER, "w", encoding="utf-8", newline="\n").write(ser)
print("serializers: school made read-only")
