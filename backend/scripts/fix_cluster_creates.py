"""Fix create-blocking serializers across reporting/conferences/auth/fees.

Rules (per serializer's model + its viewset's perform_create):
- model has `school` FK and viewset sets school -> add school to read_only_fields
- model has `school` FK and viewset bare-save -> add school read-only + save(school=...)
- model has `user` FK and viewset bare-save -> add user read-only + save(user=...)
- viewset validates a provided user (UserRole/DeviceManagement/UserSession) -> keep writable
"""

import os
import re
import sys

sys.path.insert(0, "/app")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.base")

import django

django.setup()

from services import auth, conferences, fees, reporting  # noqa: E402

MODULES = {"reporting": reporting, "conferences": conferences, "auth": auth, "fees": fees}

# viewsets that intentionally accept a user from the client (admin assignment)
USER_VALIDATING_VIEWSETS = {"UserRoleViewSet", "DeviceManagementViewSet", "UserSessionViewSet"}


def model_fields(model):
    return {f.name for f in model._meta.get_fields()}


def viewset_block(src, name):
    m = re.search(rf"class {name}\(.*?(?=\nclass |\Z)", src, re.S)
    return m.group(0) if m else None


def pc_body(block):
    m = re.search(r"def perform_create\(self, serializer\):(.*?)(?=\n    def |\Z)", block, re.S)
    return m.group(1) if m else None


for mod_name, mod in MODULES.items():
    vpath = f"services/{mod_name}/views.py"
    vsrc = open(vpath, encoding="utf-8").read().replace("\r\n", "\n")
    spath = f"services/{mod_name}/serializers.py"
    ssrc = open(spath, encoding="utf-8").read().replace("\r\n", "\n")
    sblocks = re.split(r"(?=^class \w+Serializer\()", ssrc, flags=re.M)
    view_fixes = {}  # viewset -> new perform_create body
    ser_fixes = []  # (serializer name, field)
    for sb in sblocks:
        m = re.match(r"class (\w+Serializer)\(", sb)
        if not m:
            continue
        sname = m.group(1)
        mm = re.search(r"model = (\w+)", sb)
        if not mm:
            continue
        model_name = mm.group(1)
        model = getattr(mod.models, model_name, None)
        if model is None:
            continue
        fields = model_fields(model)
        fm = re.search(r"fields = \[(.*?)\]", sb, re.S)
        if not fm:
            continue
        field_names = set(re.findall(r'"(\w+)"', fm.group(1)))
        ro = re.search(r"read_only_fields = \[(.*?)\]", sb, re.S)
        ro_fields = set(re.findall(r'"(\w+)"', ro.group(1))) if ro else set()
        vname = model_name + "ViewSet"
        vblock = viewset_block(vsrc, vname) or ""
        pcb = pc_body(vblock) or ""
        sets_school = "save(school=" in pcb
        sets_user = "save(user=" in pcb
        bare = pcb.strip() == "serializer.save()"
        validates_user = vname in USER_VALIDATING_VIEWSETS
        for f in ("school", "user"):
            if f not in field_names or f in ro_fields:
                continue
            if f == "school" and "school" in fields:
                if sets_school:
                    ser_fixes.append((sname, "school"))
                elif bare:
                    ser_fixes.append((sname, "school"))
                    view_fixes[vname] = view_fixes.get(vname, pcb).replace(
                        "serializer.save()", "serializer.save(school=self.request.user.school)"
                    )
            elif f == "user" and "user" in fields and bare and not validates_user:
                ser_fixes.append((sname, "user"))
                view_fixes[vname] = view_fixes.get(vname, pcb).replace(
                    "serializer.save()", "serializer.save(user=self.request.user)"
                )
    # apply serializer fixes
    for sname, field in ser_fixes:
        m = re.search(rf"class {sname}\(.*?(?=\nclass |\Z)", ssrc, re.S)
        block = m.group(0)
        ro = re.search(r"read_only_fields = \[(.*?)\]", block, re.S)
        if ro:
            new_block = block.replace(
                ro.group(0),
                f'read_only_fields = [{ro.group(1).rstrip()}, "{field}"]',
            )
        else:
            # insert before class Meta end
            new_block = block.replace(
                "        class Meta:",
                f'        class Meta:\n            read_only_fields = ["{field}"]',
            )
        ssrc = ssrc.replace(block, new_block)
    open(spath, "w", encoding="utf-8", newline="").write(ssrc)
    # apply viewset fixes
    for vname, new_pcb in view_fixes.items():
        m = re.search(rf"class {vname}\(.*?(?=\nclass |\Z)", vsrc, re.S)
        block = m.group(0)
        old_pc = pc_body(block)
        new_block = block.replace(old_pc, new_pcb) if old_pc else block
        vsrc = vsrc.replace(block, new_block)
    open(vpath, "w", encoding="utf-8", newline="").write(vsrc)
    print(f"{mod_name}: {len(ser_fixes)} serializer fields read-only, {len(view_fixes)} viewset fixes")
