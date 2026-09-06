"""One-shot health_clinic module fixes:
1. Make `school` read-only in serializers that expose it writable
   (all viewsets set it server-side via perform_create).
2. Add FK display fields (student_name, *_name) for the UI cards.
"""

import re

path = "services/health_clinic/serializers.py"


def add_to_fields(block, adds):
    """Insert new field names before the closing bracket of the fields list."""
    fm = re.search(r"fields = \[(.*?)\]", block, re.S)
    if not fm or not adds:
        return block
    existing = re.findall(r'"(\w+)"', fm.group(1))
    adds = [a for a in adds if a not in existing]
    if not adds:
        return block
    body = fm.group(0)
    head = body[:-1].rstrip()  # drop final ]
    if not head.endswith(","):
        head += ","
    insert = "\n            " + ", ".join(f'"{a}"' for a in adds) + "\n        ]"
    return block.replace(body, head + insert, 1)


def insert_decls(block, decls):
    """Insert serializer field declarations right after the class line."""
    if not decls:
        return block
    lines = block.split("\n")
    for li, ln in enumerate(lines):
        if ln.startswith("class "):
            insert_line = li + 1
            break
    return "\n".join(lines[:insert_line]) + "\n" + "\n".join(decls) + "\n" + "\n".join(lines[insert_line:])


src = open(path, encoding="utf-8").read()

# ─── 1. school read-only ─────────────────────────────────────────────────────
blocks = re.split(r"(?=^class \w+Serializer\()", src, flags=re.M)
changed_ro = 0
for i, block in enumerate(blocks):
    m = re.match(r"^class (\w+Serializer)\(", block)
    if not m:
        continue
    fm = re.search(r"fields = \[(.*?)\]", block, re.S)
    fields = re.findall(r'"(\w+)"', fm.group(1)) if fm else []
    if "school" not in fields:
        continue
    rm = re.search(r"read_only_fields = (\[|\()(.*?)(\]|\))", block, re.S)
    if rm:
        if '"school"' in rm.group(2):
            continue
        new_body = rm.group(2).rstrip().rstrip(",")
        new_body += (", " if new_body.strip() else "") + '"school",'
        blocks[i] = block.replace(rm.group(0), f"read_only_fields = ({new_body})")
    else:
        fm2 = re.search(r"fields = \[(.*?)\]", block, re.S)
        insert_at = fm2.end()
        blocks[i] = block[:insert_at] + '\n    read_only_fields = ["school", "id", "created_at"]' + block[insert_at:]
    changed_ro += 1

src = "".join(blocks)
print(f"school read-only: {changed_ro} serializers")

# ─── 2. FK display fields ────────────────────────────────────────────────────
# (display_name, source_path) pairs; only applied if the FK field exists.
STUDENT = ("student_name", "student.__str__")
USER_FIELDS = {
    "treated_by": "treated_by_name",
    "administered_by": "administered_by_name",
    "created_by": "created_by_name",
    "submitted_by": "submitted_by_name",
    "reviewed_by": "reviewed_by_name",
    "screened_by": "screened_by_name",
    "verified_by": "verified_by_name",
    "nurse": "nurse_name",
    "reported_by": "reported_by_name",
    "generated_by": "generated_by_name",
    "recorded_by": "recorded_by_name",
    "ordered_by": "ordered_by_name",
    "assessed_by": "assessed_by_name",
    "provider": "provider_name",
    "staff_member": "staff_member_name",
}

DISPLAY_MAP = {
    "HealthRecordSerializer": [STUDENT],
    "NurseVisitSerializer": [STUDENT, ("treated_by_name", "treated_by.get_full_name")],
    "ImmunizationSerializer": [STUDENT],
    "MedicationLogSerializer": [STUDENT, ("administered_by_name", "administered_by.get_full_name")],
    "HealthFormSerializer": [("created_by_name", "created_by.get_full_name")],
    "HealthFormSubmissionSerializer": [
        STUDENT,
        ("form_title", "form.title"),
        ("submitted_by_name", "submitted_by.get_full_name"),
        ("reviewed_by_name", "reviewed_by.get_full_name"),
    ],
    "AllergyManagementSerializer": [STUDENT],
    "ChronicConditionTrackingSerializer": [STUDENT],
    "EmergencyPlanSerializer": [("created_by_name", "created_by.get_full_name")],
    "EmergencyContactSerializer": [STUDENT],
    "HealthScreeningSerializer": [STUDENT, ("screened_by_name", "screened_by.get_full_name")],
    "ScreeningResultSerializer": [("screening_label", "screening.__str__")],
    "MedicationPrescriptionSerializer": [STUDENT],
    "ParentNotificationSerializer": [STUDENT],
    "HealthComplianceSerializer": [STUDENT, ("verified_by_name", "verified_by.get_full_name")],
    "NurseScheduleSerializer": [("nurse_name", "nurse.get_full_name")],
    "IncidentReportSerializer": [STUDENT, ("reported_by_name", "reported_by.get_full_name")],
    "MedicalReferralSerializer": [STUDENT],
    "HealthReportSerializer": [("generated_by_name", "generated_by.get_full_name")],
    "HealthAlertSerializer": [STUDENT],
    "HealthEducationSerializer": [("created_by_name", "created_by.get_full_name")],
    "TelehealthSessionSerializer": [STUDENT],
    "DentalRecordSerializer": [STUDENT],
    "VisionRecordSerializer": [STUDENT],
    "GrowthChartSerializer": [STUDENT, ("recorded_by_name", "recorded_by.get_full_name")],
    "VitalSignsSerializer": [STUDENT, ("recorded_by_name", "recorded_by.get_full_name")],
    "LabResultSerializer": [
        STUDENT,
        ("ordered_by_name", "ordered_by.get_full_name"),
        ("reviewed_by_name", "reviewed_by.get_full_name"),
    ],
    "MedicalHistorySerializer": [STUDENT],
    "FamilyMedicalHistorySerializer": [STUDENT],
    "HealthInsuranceRecordSerializer": [STUDENT],
    "VaccinationScheduleSerializer": [STUDENT],
    "HealthAssessmentSerializer": [STUDENT, ("assessed_by_name", "assessed_by.get_full_name")],
    "HealthRiskAssessmentSerializer": [STUDENT, ("assessed_by_name", "assessed_by.get_full_name")],
    "MentalHealthRecordSerializer": [STUDENT, ("provider_name", "provider.get_full_name")],
    "HealthStaffTrainingSerializer": [("staff_member_name", "staff_member.get_full_name")],
    "EquipmentMaintenanceSerializer": [("equipment_name", "equipment.name")],
}

blocks = re.split(r"(?=^class \w+Serializer\()", src, flags=re.M)
changed_disp = 0
for i, block in enumerate(blocks):
    m = re.match(r"^class (\w+Serializer)\(", block)
    if not m or m.group(1) not in DISPLAY_MAP:
        continue
    name = m.group(1)
    wanted = DISPLAY_MAP[name]
    decls = []
    adds = []
    for disp, source in wanted:
        if disp in block:
            continue
        fk = source.split(".")[0]
        # only add display if the FK itself is a serializer field
        fm = re.search(r"fields = \[(.*?)\]", block, re.S)
        existing = re.findall(r'"(\w+)"', fm.group(1))
        if fk not in existing:
            continue
        decls.append(f'    {disp} = serializers.CharField(source="{source}", read_only=True)')
        adds.append(disp)
    if not adds:
        continue
    block = insert_decls(block, decls)
    block = add_to_fields(block, adds)
    blocks[i] = block
    changed_disp += 1

src = "".join(blocks)
open(path, "w", encoding="utf-8", newline="\n").write(src)
print(f"display fields: {changed_disp} serializers")
