"""Fix transportation module: 8 viewsets filter school= on models that
scope through vehicle/driver/tracking instead.

BusTracking, GeofenceAlert, StopETA, VehicleAssignmentLog,
VehicleConditionReport, VehicleGPSLog -> vehicle__school
DriverLicense, DriverPerformance -> driver__school
Also removes the matching broken perform_create school= saves.
"""

import re

VIEWS = "services/transportation/views.py"

FIXES = {
    "BusTrackingViewSet": "vehicle__school",
    "GeofenceAlertViewSet": "vehicle__school",
    "StopETAViewSet": "tracking__vehicle__school",
    "VehicleAssignmentLogViewSet": "vehicle__school",
    "VehicleConditionReportViewSet": "vehicle__school",
    "VehicleGPSLogViewSet": "vehicle__school",
    "DriverLicenseViewSet": "driver__school",
    "DriverPerformanceViewSet": "driver__school",
}

src = open(VIEWS, encoding="utf-8").read().replace("\r\n", "\n")
blocks = re.split(r"(?=^class \w+ViewSet)", src, flags=re.M)
out = [blocks[0]]
fixed_qs = fixed_pc = 0
for b in blocks[1:]:
    m = re.match(r"^class (\w+ViewSet)", b)
    name = m.group(1) if m else ""
    if name in FIXES:
        path = FIXES[name]
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
print(f"transport: {fixed_qs} querysets fixed, {fixed_pc} broken perform_creates removed")
