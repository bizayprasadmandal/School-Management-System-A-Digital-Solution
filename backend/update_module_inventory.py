"""Generate missing admin.py, serializers.py, views.py, urls.py entries for inventory module."""

import re

MODULE = "inventory"

# Read models
with open(f"services/{MODULE}/models.py", encoding="utf-8") as f:
    models_content = f.read()
all_models = re.findall(r"class (\w+)\(models\.Model\):", models_content)

# Read existing files
with open(f"services/{MODULE}/admin.py", encoding="utf-8") as f:
    admin_content = f.read()
with open(f"services/{MODULE}/serializers.py", encoding="utf-8") as f:
    ser_content = f.read()
with open(f"services/{MODULE}/views.py", encoding="utf-8") as f:
    views_content = f.read()
with open(f"services/{MODULE}/urls.py", encoding="utf-8") as f:
    urls_content = f.read()

# Find what's already registered
registered_admin = set(re.findall(r"admin\.site\.register\((\w+)", admin_content))
registered_admin.update(re.findall(r"@admin\.register\((\w+)", admin_content))

ser_models = set(re.findall(r"model\s*=\s*(\w+)", ser_content))

view_basenames = set(re.findall(r"class (\w+)ViewSet", views_content))

url_basenames = set(re.findall(r'router\.register\([^"]*"(\w+)"', urls_content))

# Missing models for each
missing_admin = [m for m in all_models if m not in registered_admin]
missing_ser = [m for m in all_models if m not in ser_models]
missing_views = [m for m in all_models if m + "ViewSet" not in view_basenames]

print(f"Total models: {len(all_models)}")
print(f"Missing admin: {len(missing_admin)} -> {missing_admin}")
print(f"Missing serializers: {len(missing_ser)}")
print(f"Missing views: {len(missing_views)}")

# ---- Generate Admin ----
new_admin = ""
for model in missing_admin:
    var_name = model[0].lower() + model[1:] + "Admin"
    new_admin += f"""

@admin.register({model})
class {var_name}(admin.ModelAdmin):
    list_display = ["id", "school", "created_at"]
    list_filter = ["school", "is_active"] if hasattr({model}, 'is_active') else ["school"]
    search_fields = ["id"]
    readonly_fields = ["created_at"] if hasattr({model}, 'created_at') else []
"""

# Append admin registrations
if missing_admin:
    # Find the last line and append before end
    lines = admin_content.rstrip().split("\n")
    lines.append(new_admin)
    new_admin_content = "\n".join(lines) + "\n"
    with open(f"services/{MODULE}/admin.py", "w", encoding="utf-8") as f:
        f.write(new_admin_content)
    print(f"\nAdded {len(missing_admin)} admin registrations")

# ---- Generate Serializers ----
new_ser = "\n"
for model in missing_ser:
    ser_name = model + "Serializer"
    # Get model fields
    model_match = re.search(rf"class {model}\(models\.Model\):(.*?)(?=\nclass |\Z)", models_content, re.DOTALL)
    if model_match:
        fields = re.findall(r"(\w+)\s*=\s*models\.", model_match.group(1))
        field_list = [f for f in fields if f not in ("id", "Meta", "objects")]
        # Add common fields
        (
            field_list.append("created_at")
            if "created_at" not in field_list and "created_at" in model_match.group(1)
            else None
        )
        field_list_clean = [f for f in field_list if f]
    else:
        field_list_clean = ["id", "created_at"]

    fields_str = ", ".join([f'"{f}"' for f in field_list_clean[:15]])  # limit fields

    new_ser += f"""

class {ser_name}(serializers.ModelSerializer):
    class Meta:
        model = {model}
        fields = [{fields_str}]
        read_only_fields = ["id", "created_at"]
"""

# Insert before last class or append
if missing_ser:
    lines = ser_content.rstrip().split("\n")
    lines.append(new_ser)
    new_ser_content = "\n".join(lines) + "\n"
    with open(f"services/{MODULE}/serializers.py", "w", encoding="utf-8") as f:
        f.write(new_ser_content)
    print(f"Added {len(missing_ser)} serializers")

# ---- Generate Views ----
new_views = "\n"
for model in missing_views:
    view_name = model + "ViewSet"
    ser_name = model + "Serializer"
    var_name = model[0].lower() + model[1:] + "s"

    new_views += f"""

class {view_name}(viewsets.ModelViewSet):
    serializer_class = {ser_name}
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name"] if hasattr({model}, "name") else ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return {model}.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)
"""

if missing_views:
    lines = views_content.rstrip().split("\n")
    lines.append(new_views)
    new_views_content = "\n".join(lines) + "\n"
    with open(f"services/{MODULE}/views.py", "w", encoding="utf-8") as f:
        f.write(new_views_content)
    print(f"Added {len(missing_views)} viewsets")

# ---- Generate URLs ----
new_urls = ""
for model in missing_views:
    view_name = model + "ViewSet"
    var_name = model[0].lower() + model[1:] + "s"
    # Create URL slug from model name: CamelCase -> kebab-case
    slug = re.sub(r"(?<!^)(?=[A-Z])", "-", model).lower()
    # Make it plural
    if not slug.endswith("s"):
        slug += "s"
    new_urls += f'    router.register(r"{slug}", {view_name}, basename="{slug}")\n'

if missing_views:
    # Insert router.register lines
    lines = urls_content.rstrip().split("\n")
    # Find the last router.register line
    insert_idx = -1
    for i, line in enumerate(lines):
        if "router.register" in line:
            insert_idx = i
    if insert_idx >= 0:
        lines.insert(insert_idx + 1, new_urls.rstrip())
    else:
        lines.append(new_urls)
    new_urls_content = "\n".join(lines) + "\n"
    with open(f"services/{MODULE}/urls.py", "w", encoding="utf-8") as f:
        f.write(new_urls_content)
    print(f"Added {len(missing_views)} URL registrations")

# ---- Update imports in views.py ----
missing_ser_imports = [m + "Serializer" for m in missing_ser if m + "Serializer" not in views_content]

# Fix model imports in views
if "from .models import" in views_content:
    old_import = re.search(r"from \.models import (.*?)$", views_content, re.MULTILINE)
    if old_import:
        current_imports = old_import.group(1).split(",")
        current_imports = [c.strip() for c in current_imports if c.strip()]
        for m in missing_views:
            if m not in current_imports:
                current_imports.append(m)
        new_import_line = "from .models import " + ", ".join(current_imports)
        new_views_file = views_content.replace(old_import.group(0), new_import_line)
        with open(f"services/{MODULE}/views.py", "w", encoding="utf-8") as f:
            f.write(new_views_file)

# Fix serializer imports in views
if "from .serializers import" in views_content:
    with open(f"services/{MODULE}/views.py", encoding="utf-8") as f:
        v = f.read()
    old_ser_import = re.search(r"from \.serializers import (.*?)$", v, re.MULTILINE | re.DOTALL)
    if old_ser_import:
        import_text = old_ser_import.group(1)
        current_sers = re.findall(r"(\w+Serializer)", import_text)
        for s in missing_ser_imports:
            if s not in current_sers:
                current_sers.append(s)
        new_ser_import = "from .serializers import (\n    " + ",\n    ".join(current_sers) + ",\n)"
        v = v.replace(old_ser_import.group(0), new_ser_import)
        with open(f"services/{MODULE}/views.py", "w", encoding="utf-8") as f:
            f.write(v)

print("\nDone! All files updated.")
