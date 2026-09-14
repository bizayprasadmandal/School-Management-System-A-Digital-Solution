"""
Seed realistic fake data for modules not covered by the other seed commands.

Covers: behavior, alumni, library, cafeteria, transportation, inventory,
infrastructure, reporting (the modules that were empty or sparse).

Strategy:
  1. Curated anchors per module (realistic names/titles/amounts).
  2. An introspection-driven filler for the remaining models: required fields
     are resolved from FK targets seeded earlier (two passes for ordering),
     choices picked from field.choices, text shaped by field name.

Idempotent: anchors use get_or_create; the filler skips models that already
have rows for the school. Use --force to top up regardless.

Usage:
    python manage.py seed_module_data                 # all modules
    python manage.py seed_module_data --module library --module alumni
    python manage.py seed_module_data --force         # top up even if non-empty
"""

import random
from datetime import timedelta

from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import IntegrityError, transaction
from django.utils import timezone
from faker import Faker
from services.auth.models import School, User

fake = Faker()
Faker.seed(42)
random.seed(42)

MODULES = [
    "behavior",
    "alumni",
    "library",
    "cafeteria",
    "transportation",
    "inventory",
    "infrastructure",
    "reporting",
    # Modules whose older seeders left their long-tail models empty — the
    # generic filler pass covers them (UI browse confirmed the gaps).
    "sports",
    "health_clinic",
    "counseling",
    "communication",
    "admissions",
    "conferences",
    "fees",
    "attendance",
    "hr",
]

ANCHOR_COUNT = 12
CHILD_COUNT = 6

BEHAVIOR_CATEGORIES = [
    ("Disruption", "minor", -2),
    ("Tardiness", "minor", -1),
    ("Disrespect", "moderate", -3),
    ("Bullying", "major", -8),
    ("Dress Code Violation", "minor", -1),
    ("Helping Peers", "positive", 3),
    ("Academic Excellence", "positive", 5),
    ("Community Service", "positive", 4),
    ("Attendance Streak", "positive", 2),
    ("Vandalism", "major", -6),
]

BOOK_CATEGORIES = [
    "Fiction",
    "Non-Fiction",
    "Science",
    "History",
    "Reference",
    "Biography",
]
BOOK_TITLES = [
    ("To Kill a Mockingbird", "Harper Lee"),
    ("A Brief History of Time", "Stephen Hawking"),
    ("The Great Gatsby", "F. Scott Fitzgerald"),
    ("Sapiens", "Yuval Noah Harari"),
    ("Cosmos", "Carl Sagan"),
    ("Pride and Prejudice", "Jane Austen"),
    ("The Selfish Gene", "Richard Dawkins"),
    ("1984", "George Orwell"),
    ("Guns, Germs, and Steel", "Jared Diamond"),
    ("The Hobbit", "J.R.R. Tolkien"),
    ("Thinking, Fast and Slow", "Daniel Kahneman"),
    ("Jane Eyre", "Charlotte Brontë"),
]

ALUMNI_OCCUPATIONS = [
    "Software Engineer",
    "Doctor",
    "Teacher",
    "Civil Engineer",
    "Accountant",
    "Nurse",
    "Lawyer",
    "Architect",
    "Data Analyst",
    "Entrepreneur",
]

CAFETERIA_MENUS = [
    ("Pancakes & Fruit", "breakfast"),
    ("Oatmeal Bar", "breakfast"),
    ("Chicken Rice Bowl", "lunch"),
    ("Veggie Pasta", "lunch"),
    ("Grilled Cheese & Soup", "lunch"),
    ("Salad & Wrap", "lunch"),
    ("Trail Mix & Yogurt", "snack"),
    ("Fresh Fruit Cup", "snack"),
]

ROUTE_NAMES = [
    "Route A — Riverside",
    "Route B — Hillside",
    "Route C — Downtown",
    "Route D — Lakeview",
    "Route E — Forest Rd",
]

WAREHOUSE_NAMES = ["Main Warehouse", "Annex Storage", "Sports Depot"]
ITEM_NAMES = [
    "Whiteboard Markers",
    "Printer Paper",
    "Chalk Boxes",
    "Projector Bulbs",
    "Desk Chairs",
    "Lab Goggles",
    "Footballs",
    "Art Supplies",
    "Cleaning Kits",
    "First Aid Refills",
    "USB Cables",
    "Notebooks",
]

ASSET_NAMES = [
    "Science Lab",
    "Computer Lab",
    "Library Wing",
    "Auditorium",
    "Gymnasium",
    "Swimming Pool",
    "Cafeteria Block",
]


def shape_text(model_name, field, i):
    """Generate a plausible value for a text field based on its name."""
    n = field.name.lower()
    if n in {"name", "title"}:
        return f"{fake.word().capitalize()} {fake.word().capitalize()} {i}"
    if "description" in n or n in {
        "notes",
        "remarks",
        "bio",
        "summary",
        "content",
        "reason",
        "details",
    }:
        return fake.sentence(nb_words=10)
    if "email" in n:
        return fake.email()
    if "phone" in n or "mobile" in n:
        return fake.phone_number()
    if "address" in n:
        return fake.street_address()
    if "url" in n or "link" in n:
        return fake.url()
    if "code" in n or "number" in n or "sku" in n or "barcode" in n:
        return fake.bothify(text="??-####", letters="ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    if "color" in n:
        return random.choice(["#6366f1", "#22c55e", "#f59e0b", "#ef4444", "#0ea5e9"])
    if "city" in n:
        return fake.city()
    if "country" in n:
        return fake.country()
    if "status" in n:
        return "active"
    if "first_name" == n:
        return fake.first_name()
    if "last_name" == n:
        return fake.last_name()
    return fake.word().capitalize()


def shape_number(field, i):
    n = field.name.lower()
    if "year" in n:
        return random.randint(2018, 2026)
    if any(k in n for k in ("count", "total", "quantity", "capacity", "points", "copies", "pages")):
        return random.randint(1, 120)
    if "percentage" in n or "percent" in n or "rate" in n:
        # Stay under 100.0 so DecimalField(precision=3, scale=1) never overflows.
        return round(random.uniform(35, 99.5), 1)
    if "price" in n or "amount" in n or "cost" in n or "fee" in n or "salary" in n:
        return round(random.uniform(5, 900), 2)
    return random.randint(1, 50)


class Command(BaseCommand):
    help = (
        "Seed fake data for behavior, alumni, library, cafeteria, "
        "transportation, inventory, infrastructure, reporting."
    )

    def add_arguments(self, parser):
        parser.add_argument("--module", action="append", choices=MODULES)
        parser.add_argument(
            "--force",
            action="store_true",
            help="Seed even when the module already has data.",
        )

    # ─── helpers ────────────────────────────────────────────────────────────

    def model_has_school(self, model):
        return any(f.name == "school" for f in model._meta.fields)

    def required_fk_targets(self, model):
        """[(field, related_model)] for required, non-school FKs."""
        out = []
        for f in model._meta.fields:
            if f.auto_created or f.primary_key or getattr(f, "null", False):
                continue
            if f.has_default() or getattr(f, "blank", False):
                continue
            if f.is_relation and f.related_model is not None and f.name != "school":
                out.append((f, f.related_model))
        return out

    def pick_fk(self, related_model, i):
        pool = self.row_pool.get(related_model) or []
        if not pool:
            return None
        return pool[(i * 7) % len(pool)]

    def unique_field_names(self, model):
        """Fields that are unique or part of a unique_together constraint."""
        names = {f.name for f in model._meta.fields if f.unique}
        for tup in model._meta.unique_together:
            names.update(tup)
        return names

    def build_kwargs(self, model, school, i, extra=None):
        """Introspection-driven kwargs for required fields."""
        unique_fields = self.unique_field_names(model)
        kwargs = {}
        for f in model._meta.fields:
            if f.auto_created or f.primary_key or getattr(f, "null", False):
                continue
            if f.has_default():
                continue
            # Code-like unique fields (sku/code/barcode…) may be blank=True,
            # but leaving them out makes every row '' and collide. Generate.
            if getattr(f, "blank", False) and not (
                f.get_internal_type() in ("CharField", "SlugField") and f.name in unique_fields
            ):
                continue
            name = f.name
            if name == "school":
                kwargs[name] = school
            elif f.is_relation and f.related_model is not None:
                rel = self.pick_fk(f.related_model, i)
                if rel is None:
                    return None  # FK target unseedable right now
                kwargs[name] = rel
            elif f.is_relation:
                return None
            elif f.get_internal_type() in ("CharField", "TextField", "SlugField"):
                val = shape_text(model.__name__, f, i)
                if f.name in unique_fields:
                    val = f"{val}-{i}"  # unique or unique_together member
                kwargs[name] = val[: f.max_length] if getattr(f, "max_length", None) else val
            elif "IntegerField" in f.get_internal_type():
                # covers Integer/PositiveInteger/Small/PositiveSmall/Big variants
                kwargs[name] = shape_number(f, i)
            elif f.get_internal_type() == "FloatField":
                kwargs[name] = shape_number(f, i)
            elif f.get_internal_type() == "DecimalField":
                val = shape_number(f, i)
                # Respect declared precision so Postgres never overflows.
                max_digits = getattr(f, "max_digits", None) or 10
                whole = max_digits - (getattr(f, "decimal_places", 0) or 0)
                limit = (10**whole) - 1
                val = min(val, limit - 0.1) if whole else 0
                kwargs[name] = round(val, getattr(f, "decimal_places", 0) or 0)
            elif f.get_internal_type() == "JSONField":
                kwargs[name] = {}
            elif f.get_internal_type() == "DurationField":
                kwargs[name] = timedelta(minutes=random.choice([15, 30, 45, 60, 90]))
            elif f.get_internal_type() == "BooleanField":
                kwargs[name] = random.random() < 0.4
            elif f.get_internal_type() == "DateField":
                kwargs[name] = timezone.localdate() - timedelta(days=random.randint(0, 300))
            elif f.get_internal_type() == "DateTimeField":
                kwargs[name] = timezone.now() - timedelta(days=random.randint(0, 300), hours=random.randint(0, 23))
            elif f.get_internal_type() == "TimeField":
                from datetime import time

                kwargs[name] = time(random.randint(7, 17), random.choice([0, 15, 30, 45]))
            elif f.choices:
                kwargs[name] = random.choice(f.choices)[0]
            else:
                return None
        # choices may not have been hit if internal type matched first
        for name, val in list(kwargs.items()):
            f = model._meta.get_field(name)
            if f.choices and name != "school":
                kwargs[name] = random.choice(f.choices)[0]
        if extra:
            kwargs.update(extra)
        return kwargs

    def seed_model_rows(self, model, school, count, extra_fn=None):
        """Create `count` rows; returns number created. Skips if already populated."""
        qs = model.objects.all()
        if self.model_has_school(model):
            qs = qs.filter(school=school)
        if qs.exists() and not self.force:
            return 0
        created = 0
        for i in range(count):
            extra = extra_fn(i) if extra_fn else None
            kwargs = self.build_kwargs(model, school, i, extra)
            if kwargs is None:
                break
            try:
                with transaction.atomic():
                    obj = model.objects.create(**kwargs)
                created += 1
                self.row_pool.setdefault(model, []).append(obj)
            except Exception:  # noqa: BLE001 — seed tolerance: skip bad rows
                continue
        return created

    # ─── curated anchors ────────────────────────────────────────────────────

    def seed_behavior(self, school):
        BehaviorCategory = apps.get_model("behavior", "BehaviorCategory")
        Incident = apps.get_model("behavior", "Incident")
        cats = []
        for name, sev, pts in BEHAVIOR_CATEGORIES:
            cat, _ = BehaviorCategory.objects.get_or_create(
                school=school,
                name=name,
                defaults={
                    "category_type": "positive" if pts > 0 else "negative",
                    "points_value": abs(pts),
                    "is_active": True,
                },
            )
            cats.append(cat)
        self.row_pool.setdefault(BehaviorCategory, []).extend(cats)
        n = self.seed_model_rows(Incident, school, ANCHOR_COUNT)
        return f"{len(cats)} categories, {n} incidents"

    def seed_alumni(self, school):
        AlumniProfile = apps.get_model("alumni", "AlumniProfile")
        qs = AlumniProfile.objects.filter(school=school)
        if qs.exists() and not self.force:
            return f"skipped ({qs.count()} exist)"
        made = 0
        for i in range(ANCHOR_COUNT):
            email = f"alumni{i + 1}.{fake.last_name().lower()}@alumni.gvs.edu"
            if User.objects.filter(email=email).exists():
                continue
            user = User.objects.create_user(
                email=email,
                password="Alumni@1234",
                school=school,
                role="alumni",
                first_name=fake.first_name(),
                last_name=fake.last_name(),
            )
            try:
                profile = AlumniProfile.objects.create(
                    school=school,
                    user=user,
                    graduation_year=random.randint(2012, 2025),
                    occupation=ALUMNI_OCCUPATIONS[i % len(ALUMNI_OCCUPATIONS)],
                    city=fake.city(),
                    country=fake.country(),
                )
                made += 1
                self.row_pool.setdefault(AlumniProfile, []).append(profile)
            except IntegrityError:
                user.delete()
        return f"{made} alumni profiles (+login users, password Alumni@1234)"

    def seed_library(self, school):
        BookCategory = apps.get_model("library", "BookCategory")
        Book = apps.get_model("library", "Book")
        cats = []
        for name in BOOK_CATEGORIES:
            cat, _ = BookCategory.objects.get_or_create(school=school, name=name)
            cats.append(cat)
        self.row_pool.setdefault(BookCategory, []).extend(cats)
        existing = Book.objects.filter(school=school).count()
        made = 0
        if existing < ANCHOR_COUNT or self.force:
            for i, (title, author) in enumerate(BOOK_TITLES):
                if Book.objects.filter(school=school, title=title).exists():
                    continue
                book = Book.objects.create(
                    school=school,
                    title=title,
                    author=author,
                    isbn=f"978-{random.randint(10**9, 10**10 - 1)}",
                    category=cats[i % len(cats)],
                    total_copies=random.randint(2, 8),
                    available_copies=random.randint(1, 5),
                )
                made += 1
                self.row_pool.setdefault(Book, []).append(book)
        n_children = 0
        for mname in ("BookCopy", "Checkout", "BookReservation", "FineManagement"):
            try:
                n_children += self.seed_model_rows(apps.get_model("library", mname), school, CHILD_COUNT)
            except LookupError:
                pass
        return f"{len(cats)} categories, {made} books, {n_children} loans/copies/reserves/fines"

    def seed_cafeteria(self, school):
        MealMenu = apps.get_model("cafeteria", "MealMenu")
        existing = MealMenu.objects.filter(school=school).count()
        made = 0
        if existing < ANCHOR_COUNT or self.force:
            for i, (name, meal) in enumerate(CAFETERIA_MENUS):
                try:
                    with transaction.atomic():
                        menu = MealMenu.objects.create(
                            school=school,
                            name=name,
                            meal_type=meal,
                            date=timezone.localdate() + timedelta(days=i - 6),
                        )
                    made += 1
                    self.row_pool.setdefault(MealMenu, []).append(menu)
                except (IntegrityError, TypeError):
                    continue
        n = 0
        for mname in ("MealPlan", "MealBooking", "FoodSafetyIncident"):
            try:
                n += self.seed_model_rows(apps.get_model("cafeteria", mname), school, CHILD_COUNT)
            except LookupError:
                pass
        return f"{made} menus, {n} plans/bookings/incidents"

    def seed_transportation(self, school):
        Route = apps.get_model("transportation", "Route")
        made = 0
        for name in ROUTE_NAMES:
            if Route.objects.filter(school=school, name=name).exists():
                continue
            try:
                route = Route.objects.create(school=school, name=name)
                made += 1
                self.row_pool.setdefault(Route, []).append(route)
            except (IntegrityError, TypeError):
                continue
        n = 0
        for mname in ("Stop", "Vehicle", "Driver", "StudentRide"):
            try:
                n += self.seed_model_rows(apps.get_model("transportation", mname), school, CHILD_COUNT)
            except LookupError:
                pass
        return f"{made} routes, {n} stops/vehicles/drivers/rides"

    def seed_inventory(self, school):
        Warehouse = apps.get_model("inventory", "Warehouse")
        Item = apps.get_model("inventory", "InventoryItem")
        warehouses = []
        for idx, name in enumerate(WAREHOUSE_NAMES):
            w, _ = Warehouse.objects.get_or_create(
                school=school,
                name=name,
                defaults={"code": f"WH-{idx + 1:02d}"},
            )
            warehouses.append(w)
        self.row_pool.setdefault(Warehouse, []).extend(warehouses)
        made = 0
        existing = Item.objects.filter(school=school).count()
        if existing < len(ITEM_NAMES) or self.force:

            def item_extra(i):
                name = ITEM_NAMES[i % len(ITEM_NAMES)]
                if i >= len(ITEM_NAMES):
                    name = f"{name} {i}"  # keep names unique on re-seeds
                return {"name": name}

            made = self.seed_model_rows(Item, school, len(ITEM_NAMES), extra_fn=item_extra)
        n = 0
        for mname in ("Category", "Supplier", "StockLevel", "PurchaseOrder"):
            try:
                n += self.seed_model_rows(apps.get_model("inventory", mname), school, CHILD_COUNT)
            except LookupError:
                pass
        return f"{len(warehouses)} warehouses, {made} items, {n} stock/suppliers/POs"

    def seed_infrastructure(self, school):
        made = 0
        Building = None
        for candidate in ("Building", "Facility", "Asset"):
            try:
                Building = apps.get_model("infrastructure", candidate)
                break
            except LookupError:
                continue
        if Building:
            made = self.seed_model_rows(Building, school, 7)
        n = 0
        for mname in ("MaintenanceRequest", "WorkOrder", "Room", "UtilityMeter"):
            try:
                n += self.seed_model_rows(apps.get_model("infrastructure", mname), school, CHILD_COUNT)
            except LookupError:
                pass
        return f"{made} buildings, {n} maintenance/rooms/meters"

    def seed_reporting(self, school):
        made = 0
        for mname in (
            "ReportDefinition",
            "SavedReport",
            "ScheduledReport",
            "Dashboard",
        ):
            try:
                made += self.seed_model_rows(apps.get_model("reporting", mname), school, 4)
            except LookupError:
                continue
        return f"{made} report definitions/dashboards"

    SEEDERS = {
        "behavior": seed_behavior,
        "alumni": seed_alumni,
        "library": seed_library,
        "cafeteria": seed_cafeteria,
        "transportation": seed_transportation,
        "inventory": seed_inventory,
        "infrastructure": seed_infrastructure,
        "reporting": seed_reporting,
    }

    # ─── generic filler pass ────────────────────────────────────────────────

    def filler_pass(self, school, modules, pass_no):
        filled = {}
        for app_label in modules:
            try:
                config = apps.get_app_config(app_label)
            except LookupError:
                continue
            models = sorted(
                config.get_models(),
                key=lambda m: (len(self.required_fk_targets(m)), m.__name__),
            )
            for model in models:
                if model in self.attempted and not self.force:
                    continue
                self.attempted.add(model)
                try:
                    n = self.seed_model_rows(model, school, CHILD_COUNT)
                except Exception:  # noqa: BLE001 — one bad model must not kill the pass
                    n = 0
                if n:
                    filled[model.__name__] = n
        return filled

    def handle(self, *args, **options):
        self.force = options.get("force", False)
        modules = options.get("module") or MODULES
        school = School.objects.first()
        if not school:
            self.stderr.write("No school exists — run seed_demo_data first.")
            return

        self.row_pool = {}
        self.attempted = set()
        # Preload existing rows so FK resolution can use them — including
        # cross-module targets (students, users) that child models point at.
        POOL_APPS = list(modules) + ["students"]
        for app_label in dict.fromkeys(POOL_APPS):
            try:
                for m in apps.get_app_config(app_label).get_models():
                    qs = m.objects.all()
                    if self.model_has_school(m):
                        qs = qs.filter(school=school)
                    rows = list(qs[:50])
                    if rows:
                        self.row_pool[m] = rows
            except LookupError:
                continue
        # Pool the User model explicitly: it does not live in the built-in
        # "auth" app config, and User-FK models (Employee, counselor, teacher
        # availability…) silently fail to seed without it.
        user_qs = User.objects.all()
        if self.model_has_school(User):
            user_qs = user_qs.filter(school=school)
        user_rows = list(user_qs[:50])
        if user_rows:
            self.row_pool[User] = user_rows

        self.stdout.write(f"Seeding {len(modules)} modules for {school}…")
        for mod in modules:
            seeder = self.SEEDERS.get(mod)
            if seeder:
                try:
                    summary = seeder(self, school)
                    self.stdout.write(self.style.SUCCESS(f"  {mod:<15} {summary}"))
                except Exception as exc:  # noqa: BLE001
                    self.stdout.write(self.style.ERROR(f"  {mod:<15} FAILED: {exc}"))

        filled = self.filler_pass(school, modules, 1)
        filled2 = self.filler_pass(school, modules, 2)
        merged = {**filled2, **filled}

        total = sum(merged.values())
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"Filler pass: {total} rows across {len(merged)} models"))
        for name, n in sorted(merged.items()):
            self.stdout.write(f"    {name}: {n}")
        self.stdout.write(self.style.SUCCESS("Done."))
