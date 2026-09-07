"""Fix the writable-school create blocker in the students module.

1. Add "school" to read_only_fields in the serializers that expose it as a
   writable required field (viewsets set it server-side via perform_create).
2. Add perform_create to the two viewsets missing it (Classroom, Grade).
"""

import re

SER_PATH = "services/students/serializers.py"
VIEW_PATH = "services/students/views.py"

SERIALIZERS = [
    "AcademicYearSerializer",
    "GradeSerializer",
    "ClassroomSerializer",
    "StudentSerializer",
    "ParentProfileSerializer",
    "StudentCustomFieldSerializer",
    "StudentCategorySerializer",
    "StudentTagSerializer",
    "StudentArchiveSerializer",
    "StudentWellnessSerializer",
    "StudentLearningStyleSerializer",
    "StudentAchievementSerializer",
    "StudentClubSerializer",
    "StudentActivitySerializer",
    "StudentAwardSerializer",
    "StudentDisciplineSerializer",
    "StudentTutoringSerializer",
    "StudentMentorSerializer",
    "StudentCareerGuidanceSerializer",
    "StudentParentCommunicationSerializer",
    "StudentAcademicAdvisorSerializer",
    "StudentTransferSerializer",
    "StudentGraduationSerializer",
    "StudentVolunteerSerializer",
    "StudentInternshipSerializer",
    "StudentScholarshipSerializer",
    "StudentFinancialAidSerializer",
    "StudentTransportAssignmentSerializer",
    "StudentMealPlanSerializer",
    "StudentParkingSerializer",
    "StudentIDActivitySerializer",
    "StudentFeedbackSerializer",
]

src = open(SER_PATH, encoding="utf-8").read()
changed = 0

for cls_name in SERIALIZERS:
    m = re.search(rf"class {cls_name}\(serializers\.\w+\):", src)
    if not m:
        print("skip missing class:", cls_name)
        continue
    block_start = m.end()
    n = re.search(r"\nclass \w+", src[block_start:])
    block_end = block_start + n.start() if n else len(src)
    block = src[block_start:block_end]

    ro = re.search(r"read_only_fields = \[(.*?)\]", block, re.S)
    if ro:
        if '"school"' in ro.group(1) or "'school'" in ro.group(1):
            continue
        new_block = block.replace(ro.group(0), ro.group(0).replace("[", '["school", ', 1), 1)
        src = src[:block_start] + new_block + src[block_end:]
        changed += 1
    else:
        # append a read_only_fields line just before the block end
        insert = '\n    read_only_fields = ["school"]\n'
        src = src[:block_end] + insert + src[block_end:]
        changed += 1

open(SER_PATH, "w", encoding="utf-8").write(src)
print("serializers updated:", changed)

# ── viewsets: add perform_create where missing ──
vsrc = open(VIEW_PATH, encoding="utf-8").read()
PC = "\n    def perform_create(self, serializer):\n" "        serializer.save(school=self.request.user.school)\n"
vchanged = 0
for vs_name in ["ClassroomViewSet", "GradeViewSet"]:
    m = re.search(rf"class {vs_name}\(viewsets\.ModelViewSet\):", vsrc)
    if not m:
        print("skip missing viewset:", vs_name)
        continue
    bstart = m.end()
    n = re.search(r"\nclass \w+", vsrc[bstart:])
    bend = bstart + n.start() if n else len(vsrc)
    seg = vsrc[bstart:bend]
    if "perform_create" in seg:
        continue
    # insert after the get_permissions method block (end of segment is fine)
    vsrc = vsrc[:bend] + PC + vsrc[bend:]
    vchanged += 1

open(VIEW_PATH, "w", encoding="utf-8").write(vsrc)
print("viewsets updated:", vchanged)
