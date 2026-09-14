"""Fix hostel module: 13 viewsets filter school= on models without a school FK.

All scope through a parent: hostel (direct or via room/asset/event) or
student. Rewrite each get_queryset with the correct path and fix the
matching perform_create school= saves.
"""

import re

VIEWS = "services/hostel/views.py"

# viewset -> (queryset filter path, create strategy)
#   create: "school"  -> serializer.save(school=...)
#           "hostel"  -> cannot auto-set (needs hostel from payload); leave
#           None      -> no perform_create change
FIXES = {
    "RoommateAssignmentViewSet": ("room__hostel__school", "skip"),
    "RoomKeyViewSet": ("room__hostel__school", "skip"),
    "CommonAreaBookingViewSet": ("hostel__school", "skip"),
    "RoommateMatchRequestViewSet": ("requester__school", "skip"),
    "MessMenuPlanViewSet": ("hostel__school", "skip"),
    "HostelAssetViewSet": ("hostel__school", "skip"),
    "HostelAssetTransferViewSet": ("asset__hostel__school", "skip"),
    "HostelEventViewSet": ("hostel__school", "skip"),
    "HostelEventParticipantViewSet": ("event__hostel__school", "skip"),
    "HostelEmergencyProtocolViewSet": ("hostel__school", "skip"),
    "HostelEmergencyDrillViewSet": ("hostel__school", "skip"),
    "HostelInspectionScheduleViewSet": ("hostel__school", "skip"),
    "MessFeedbackViewSet": ("hostel__school", "skip"),
}

src = open(VIEWS, encoding="utf-8").read().replace("\r\n", "\n")
blocks = re.split(r"(?=^class \w+ViewSet)", src, flags=re.M)
out = [blocks[0]]
fixed_qs = fixed_pc = 0
for b in blocks[1:]:
    m = re.match(r"^class (\w+ViewSet)", b)
    name = m.group(1) if m else ""
    if name in FIXES:
        path, _ = FIXES[name]
        new_qs = f"return {name[:-len('ViewSet')]}.objects.filter({path}=self.request.user.school)"
        b2 = re.sub(
            r"return \w+\.objects\.filter\(school=self\.request\.user\.school\)",
            new_qs,
            b,
            count=1,
        )
        if b2 != b:
            fixed_qs += 1
            b = b2
        # perform_create: school= on a model without school FK must go
        if "serializer.save(school=self.request.user.school)" in b:
            b = b.replace(
                "    def perform_create(self, serializer):\n"
                "        serializer.save(school=self.request.user.school)\n",
                "",
            )
            fixed_pc += 1
    out.append(b)
src = "".join(out)
open(VIEWS, "w", encoding="utf-8", newline="\n").write(src)
print(f"hostel: {fixed_qs} querysets fixed, {fixed_pc} broken perform_creates removed")
