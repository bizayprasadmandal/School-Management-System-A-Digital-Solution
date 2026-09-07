"""One-shot counseling module fixes:

1. Fix 4 viewsets with wrong filter paths (FieldError on list):
   - ScreeningResponseViewSet: school= -> screening__school=
   - CrisisFollowUpViewSet: intervention__school= -> crisis__school=
   - ProgressMilestoneViewSet: tracking__school= -> progress__school=
   - InterventionGoalViewSet: plan__school= -> intervention_plan__school=
2. Register the 31 unregistered viewsets in the router.
3. Add get_queryset tenant scoping to viewsets that use the bare queryset attr
   (they would otherwise leak other schools' data).
4. Add perform_create to viewsets whose model has a school FK (creates crash
   or spoof otherwise) and child-FK viewsets keep default create.
5. Add FK display fields to serializers missing them for UI cards.
"""

import re

VIEWS = "services/counseling/views.py"
URLS = "services/counseling/urls.py"
SERS = "services/counseling/serializers.py"

views_src = open(VIEWS, encoding="utf-8").read()
urls_src = open(URLS, encoding="utf-8").read()
ser_src = open(SERS, encoding="utf-8").read()

# ---------------------------------------------------------------------------
# 1. Fix wrong filter paths
# ---------------------------------------------------------------------------
FILTER_FIXES = [
    (
        "class ScreeningResponseViewSet",
        "return ScreeningResponse.objects.filter(school=self.request.user.school)",
        "return ScreeningResponse.objects.filter(screening__school=self.request.user.school)",
    ),
    (
        "class CrisisFollowUpViewSet",
        "return CrisisFollowUp.objects.filter(intervention__school=self.request.user.school)",
        "return CrisisFollowUp.objects.filter(crisis__school=self.request.user.school)",
    ),
    (
        "class ProgressMilestoneViewSet",
        "return ProgressMilestone.objects.filter(tracking__school=self.request.user.school)",
        "return ProgressMilestone.objects.filter(progress__school=self.request.user.school)",
    ),
    (
        "class InterventionGoalViewSet",
        "return InterventionGoal.objects.filter(plan__school=self.request.user.school)",
        "return InterventionGoal.objects.filter(intervention_plan__school=self.request.user.school)",
    ),
]

for anchor, old, new in FILTER_FIXES:
    seg_start = views_src.index(anchor)
    seg_end = views_src.find("\nclass ", seg_start + 1)
    seg = views_src[seg_start:seg_end]
    assert old in seg, f"filter not found in {anchor}: {old}"
    views_src = views_src[:seg_start] + seg.replace(old, new) + views_src[seg_end:]
    print("filter fix:", anchor.split("ViewSet")[0].replace("class ", ""))

# ---------------------------------------------------------------------------
# 2/3/4. Scope + perform_create for viewsets using the bare queryset attr
# ---------------------------------------------------------------------------
# model -> (queryset model name, scoping path, has school FK, extra create kwargs)
MODEL_INFO = {
    "AcademicAdvising": ("AcademicAdvising", "school", True),
    "BullyingFollowUp": ("BullyingFollowUp", "report__school", False),
    "BullyingReport": ("BullyingReport", "school", True),
    "CareerAssessment": ("CareerAssessment", "school", True),
    "CareerGoal": ("CareerGoal", "school", True),
    "CaseNote": ("CaseNote", "case__school", False),
    "CollegeApplication": ("CollegeApplication", "school", True),
    "CounselingContract": ("CounselingContract", "school", True),
    "CounselingGoalTracking": ("CounselingGoalTracking", "school", True),
    "CounselingNotification": ("CounselingNotification", "school", True),
    "CounselingSessionLog": ("CounselingSessionLog", "school", True),
    "CounselingSurvey": ("CounselingSurvey", "school", True),
    "CounselingSurveyResponse": ("CounselingSurveyResponse", "survey__school", False),
    "CounselingWaitlist": ("CounselingWaitlist", "school", True),
    "CounselingWorkshop": ("CounselingWorkshop", "school", True),
    "CounselorAbsence": ("CounselorAbsence", "school", True),
    "CounselorCoverage": ("CounselorCoverage", "school", True),
    "CounselorProfile": ("CounselorProfile", "school", True),
    "CourseRecommendation": ("CourseRecommendation", "advising__school", False),
    "ExternalReferralProvider": ("ExternalReferralProvider", "school", True),
    "GroupSessionMember": ("GroupSessionMember", "group_session__school", False),
    "PeerMentor": ("PeerMentor", "school", True),
    "PeerMentoringSession": ("PeerMentoringSession", "mentor__school", False),
    "ReferralTracking": ("ReferralTracking", "school", True),
    "RestorativeCommitment": ("RestorativeCommitment", "session__school", False),
    "RestorativeJusticeSession": ("RestorativeJusticeSession", "school", True),
    "SELAssessment": ("SELAssessment", "school", True),
    "SELGoal": ("SELGoal", "school", True),
    "SessionAttachment": ("SessionAttachment", "session__school", False),
    "SpecialEducationReferral": ("SpecialEducationReferral", "school", True),
    "WorkshopRegistration": ("WorkshopRegistration", "workshop__school", False),
}

GQ_TEMPLATE = """
    def get_queryset(self):
        return {model}.objects.filter({path}=self.request.user.school)
"""

PC_TEMPLATE = """
    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)
"""

scoped = 0
for vs_name, (model, path, has_school) in MODEL_INFO.items():
    anchor = f"class {vs_name}ViewSet"
    if anchor not in views_src:
        print("!! viewset not found:", vs_name)
        continue
    seg_start = views_src.index(anchor)
    seg_end = views_src.find("\nclass ", seg_start + 1)
    if seg_end == -1:
        seg_end = len(views_src)
    seg = views_src[seg_start:seg_end]
    if "def get_queryset" in seg:
        print("skip (already scoped):", vs_name)
        continue
    gq = GQ_TEMPLATE.format(model=model, path=path)
    # insert right after the filter_backends/filterset/search block, i.e. before
    # the first blank-blank after permission/filter attrs — simplest: before the
    # trailing part of the class body. We insert after the last attribute line.
    lines = seg.rstrip("\n").split("\n")
    # find last contiguous attribute line (starts with 4 spaces + name =)
    insert_at = None
    for i in range(len(lines) - 1, 0, -1):
        line = lines[i]
        if re.match(r"^    \w+ = ", line):
            insert_at = i + 1
            break
    if insert_at is None:
        print("!! no attr anchor in", vs_name)
        continue
    new_seg = "\n".join(lines[:insert_at]) + "\n" + gq.strip("\n") + "\n" + "\n".join(lines[insert_at:])
    if has_school and "def perform_create" not in new_seg:
        new_seg = new_seg.rstrip("\n") + "\n" + PC_TEMPLATE.strip("\n") + "\n"
    views_src = views_src[:seg_start] + new_seg + views_src[seg_end:]
    scoped += 1
    print("scoped:", vs_name, "| path:", path, "| perform_create:", has_school)

print(f"scoped {scoped} viewsets")

# ---------------------------------------------------------------------------
# 2. Register missing routes
# ---------------------------------------------------------------------------
ROUTE_NAMES = {
    "AcademicAdvising": "academic-advising",
    "BullyingFollowUp": "bullying-followups",
    "BullyingReport": "bullying-reports",
    "CareerAssessment": "career-assessments",
    "CareerGoal": "career-goals",
    "CaseNote": "case-notes",
    "CollegeApplication": "college-applications",
    "CounselingContract": "contracts",
    "CounselingGoalTracking": "goal-tracking",
    "CounselingNotification": "notifications",
    "CounselingSessionLog": "session-logs",
    "CounselingSurvey": "surveys",
    "CounselingSurveyResponse": "survey-responses",
    "CounselingWaitlist": "waitlist",
    "CounselingWorkshop": "workshops",
    "CounselorAbsence": "absences",
    "CounselorCoverage": "coverage",
    "CounselorProfile": "counselor-profiles",
    "CourseRecommendation": "course-recommendations",
    "ExternalReferralProvider": "providers",
    "GroupSessionMember": "group-members",
    "PeerMentor": "peer-mentors",
    "PeerMentoringSession": "peer-mentoring-sessions",
    "ReferralTracking": "referral-tracking",
    "RestorativeCommitment": "restorative-commitments",
    "RestorativeJusticeSession": "restorative-sessions",
    "SELAssessment": "sel-assessments",
    "SELGoal": "sel-goals",
    "SessionAttachment": "session-attachments",
    "SpecialEducationReferral": "special-education-referrals",
    "WorkshopRegistration": "workshop-registrations",
}

new_routes = []
for model, slug in ROUTE_NAMES.items():
    vs = f"views.{model}ViewSet"
    if vs not in urls_src:
        new_routes.append(f'router.register(r"{slug}", {vs}, basename="{slug.replace("-", "_")}")')
        print("route:", slug)

if new_routes:
    # insert after the last existing router.register line
    matches = list(re.finditer(r"^router\.register\(.*\)$", urls_src, re.M))
    last = matches[-1]
    insert_pos = last.end()
    urls_src = urls_src[:insert_pos] + "\n" + "\n".join(new_routes) + urls_src[insert_pos:]

open(VIEWS, "w", encoding="utf-8", newline="\n").write(views_src)
open(URLS, "w", encoding="utf-8", newline="\n").write(urls_src)

# ---------------------------------------------------------------------------
# 5. Display fields for serializers missing them
# ---------------------------------------------------------------------------
DISPLAY_FIELDS = {
    # serializer: list of (field_name, source) to add
    "InterventionGoalSerializer": [("plan_title", "intervention_plan.title")],
    "ScreeningResponseSerializer": [("screening_title", "screening.screening_type")],
    "ProgressMilestoneSerializer": [("progress_domain", "progress.domain")],
    "CourseRecommendationSerializer": [("course_name", "course_name")],  # has own name; add advising display
    "CounselingWorkshopSerializer": [],  # has title already
    "ExternalReferralProviderSerializer": [],  # has name
    "BullyingFollowUpSerializer": [("report_type", "report.report_type")],
    "RestorativeJusticeSessionSerializer": [],
    "CounselingSurveySerializer": [],  # has title
    "CounselorCoverageSerializer": [
        ("absent_counselor_name", "absent_counselor.full_name"),
        ("covering_counselor_name", "covering_counselor.full_name"),
    ],
}

# CourseRecommendation: advising display instead
DISPLAY_FIELDS["CourseRecommendationSerializer"] = [("advising_type", "advising.advising_type")]

for ser_name, fields in DISPLAY_FIELDS.items():
    if not fields:
        continue
    anchor = f"class {ser_name}"
    if anchor not in ser_src:
        print("!! serializer not found:", ser_name)
        continue
    seg_start = ser_src.index(anchor)
    seg_end = ser_src.find("\nclass ", seg_start + 1)
    if seg_end == -1:
        seg_end = len(ser_src)
    seg = ser_src[seg_start:seg_end]
    decls = []
    for fname, fsource in fields:
        if re.search(rf"{fname}\s*=", seg):
            print("skip existing:", ser_name, fname)
            continue
        decls.append(f'    {fname} = serializers.CharField(source="{fsource}", read_only=True)')
    if not decls:
        continue
    # insert after the class declaration line
    cls_line_end = seg.index("\n") + 1
    new_seg = seg[:cls_line_end] + "\n".join(decls) + "\n" + seg[cls_line_end:]
    ser_src = ser_src[:seg_start] + new_seg + ser_src[seg_end:]
    print("display:", ser_name, [f[0] for f in fields])

    # extend fields list if it's an explicit list
    fm = re.search(r"fields\s*=\s*\[(.*?)\]", new_seg, re.S)
    if fm:
        fl = fm.group(1)
        add = [f'"{f[0]}"' for f in fields if f'"{f[0]}"' not in fl]
        if add:
            new_fl = fl.rstrip() + ",\n            " + ", ".join(add) + ","
            new_seg2 = new_seg[: fm.start(1)] + new_fl + new_seg[fm.end(1) :]
            ser_src = ser_src[:seg_start] + new_seg2 + ser_src[seg_end:]

open(SERS, "w", encoding="utf-8", newline="\n").write(ser_src)
print("done")
