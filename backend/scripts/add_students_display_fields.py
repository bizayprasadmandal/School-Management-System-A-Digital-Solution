"""Add FK display fields to students serializers that lack them.

Adds *_name CharFields (and inserts them into explicit fields lists) so the
Students Center UI cards can show human-readable titles.
"""

import re

PATH = "services/students/serializers.py"

# serializer class -> list of (field_name, source)
DISPLAY_FIELDS = {
    "StudentGuardianSerializer": [
        ("student_name", "student.full_name"),
        ("guardian_name", "guardian.full_name"),
    ],
    "EnrollmentSerializer": [
        ("student_name", "student.full_name"),
        ("classroom_name", "classroom.__str__"),
    ],
    "DocumentSerializer": [("student_name", "student.full_name")],
    "StudentCustomFieldValueSerializer": [
        ("student_name", "student.full_name"),
        ("field_name", "field.name"),
    ],
    "StudentPhotoSerializer": [("student_name", "student.full_name")],
    "StudentIDCardSerializer": [("student_name", "student.full_name")],
    "StudentStatusHistorySerializer": [("student_name", "student.full_name")],
    "SiblingTrackingSerializer": [
        ("student_name", "student.full_name"),
        ("sibling_name", "sibling.full_name"),
    ],
    "StudentCategoryMembershipSerializer": [
        ("student_name", "student.full_name"),
        ("category_name", "category.name"),
    ],
    "StudentTagAssignmentSerializer": [
        ("student_name", "student.full_name"),
        ("tag_name", "tag.name"),
    ],
    "StudentNoteSerializer": [("student_name", "student.full_name")],
    "StudentArchiveSerializer": [("student_name", "student.full_name")],
    "StudentPortfolioSerializer": [("student_name", "student.full_name")],
    "StudentWellnessSerializer": [("student_name", "student.full_name")],
    "StudentContactSerializer": [("student_name", "student.full_name")],
    "StudentMedicalRecordSerializer": [("student_name", "student.full_name")],
    "StudentSocialMediaSerializer": [("student_name", "student.full_name")],
    "StudentAchievementSerializer": [("student_name", "student.full_name")],
    "StudentActivitySerializer": [("student_name", "student.full_name")],
    "StudentClubSerializer": [("student_name", "student.full_name")],
    "StudentAwardSerializer": [("student_name", "student.full_name")],
    "StudentDisciplineSerializer": [("student_name", "student.full_name")],
    "StudentTutoringSerializer": [("student_name", "student.full_name")],
    "StudentMentorSerializer": [("student_name", "student.full_name")],
    "StudentCareerGuidanceSerializer": [("student_name", "student.full_name")],
    "StudentAcademicAdvisorSerializer": [("student_name", "student.full_name")],
    "StudentTransferSerializer": [("student_name", "student.full_name")],
    "StudentGraduationSerializer": [("student_name", "student.full_name")],
    "StudentVolunteerSerializer": [("student_name", "student.full_name")],
    "StudentInternshipSerializer": [("student_name", "student.full_name")],
    "StudentScholarshipSerializer": [("student_name", "student.full_name")],
    "StudentFinancialAidSerializer": [("student_name", "student.full_name")],
    "StudentMealPlanSerializer": [("student_name", "student.full_name")],
    "StudentParkingSerializer": [("student_name", "student.full_name")],
    "StudentIDActivitySerializer": [("student_name", "student.full_name")],
    "StudentFeedbackSerializer": [("student_name", "student.full_name")],
    "StudentLearningStyleSerializer": [("student_name", "student.full_name")],
    "StudentParentCommunicationSerializer": [("student_name", "student.full_name")],
    "StudentTransportAssignmentSerializer": [("student_name", "student.full_name")],
}

src = open(PATH, encoding="utf-8").read()
changed = 0

for cls_name, fields in DISPLAY_FIELDS.items():
    # locate the class block
    m = re.search(rf"class {cls_name}\(serializers\.\w+\):", src)
    if not m:
        print("skip missing class:", cls_name)
        continue
    block_start = m.end()
    next_cls = re.search(r"\nclass \w+", src[block_start:])
    block_end = block_start + next_cls.start() if next_cls else len(src)
    block = src[block_start:block_end]

    # only add fields that don't already exist in this block
    new_decls = []
    new_names = []
    for fname, source in fields:
        if fname in block:
            continue
        new_decls.append(f'    {fname} = serializers.CharField(source="{source}", read_only=True)')
        new_names.append(fname)

    if not new_decls:
        continue

    # insert declarations after the class header line
    decls = "\n" + "\n".join(new_decls) + "\n"
    src = src[:block_start] + decls + src[block_start:]
    changed += 1

    # re-locate block and insert names into explicit fields list
    m2 = re.search(rf"class {cls_name}\(serializers\.\w+\):", src)
    b2s = m2.end()
    n2 = re.search(r"\nclass \w+", src[b2s:])
    b2e = b2s + n2.start() if n2 else len(src)
    blk = src[b2s:b2e]
    fm = re.search(r"fields = \[", blk)
    if fm:
        insert_at = b2s + fm.end()
        src = src[:insert_at] + "".join(f'\n        "{n}",' for n in new_names) + src[insert_at:]

open(PATH, "w", encoding="utf-8").write(src)
print("updated serializers:", changed)
