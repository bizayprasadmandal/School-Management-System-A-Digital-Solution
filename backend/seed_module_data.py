"""
Seed demo data for all newly built modules (Sports, Health, Alumni, Cafeteria,
Admissions, Hostel, Transportation, Inventory).

Run inside the Docker container:
    docker exec -i sms_backend python manage.py shell < backend/seed_module_data.py
"""
import os
import sys
import uuid
from datetime import date, datetime, timedelta
from decimal import Decimal
from random import choice, randint, uniform, sample

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.development")
import django
django.setup()

from django.contrib.auth import get_user_model
from services.students.models import Student, Grade, Classroom
from services.auth.models import School, UserRole

print("Resolving demo school and users...")
school = School.objects.get(subdomain="demo")
admin = get_user_model().objects.get(school=school, role=UserRole.SCHOOL_ADMIN)
teachers = list(get_user_model().objects.filter(school=school, role=UserRole.TEACHER))
students = list(Student.objects.filter(school=school))
print(f"  School: {school.name}")
print(f"  Admin:  {admin.email}")
print(f"  Teachers: {len(teachers)}")
print(f"  Students: {len(students)}")

current_year = date.today().year

# ─────────────────────────────────────────────────────────────────────────────
# 1. SPORTS & EXTRACURRICULARS
# ─────────────────────────────────────────────────────────────────────────────
print("\n=== SPORTS & EXTRACURRICULARS ===")
from services.sports.models import Sport, Team, TeamMember, SportEvent, SportAchievement

SPORT_DATA = [
    ("Basketball", "sport", "Indoor basketball", 5, 15),
    ("Football", "sport", "Association football", 11, 22),
    ("Volleyball", "sport", "Indoor volleyball", 6, 12),
    ("Chess Club", "club", "Competitive chess", 1, 20),
    ("Debate Society", "academic", "Public speaking and debate", 2, 30),
    ("Drama Club", "arts", "Theatre and performance", 5, 25),
    ("Athletics", "sport", "Track and field", 1, 40),
    ("Swimming", "sport", "Competitive swimming", 1, 20),
    ("Music Band", "arts", "School band and orchestra", 5, 50),
    ("Science Club", "academic", "STEM activities", 2, 30),
]

for name, cat, desc, min_p, max_p in SPORT_DATA:
    Sport.objects.get_or_create(
        school=school, name=name,
        defaults=dict(category=cat, description=desc, min_players=min_p, max_players=max_p, is_active=True),
    )
sports = list(Sport.objects.filter(school=school))
print(f"  Created {len(sports)} sports/activities")

TEAM_DATA = [
    ("Varsity Boys", "boys", "Varsity Boys Basketball"),
    ("Varsity Girls", "girls", "Varsity Girls Basketball"),
    ("Junior Varsity", "mixed", "JV Basketball Team"),
    ("First XI", "mixed", "First Football XI"),
    ("Varsity Team", "mixed", "Varsity Volleyball Team"),
    ("Chess A-Team", "mixed", "Competitive Chess Team"),
]
for name, gender, sport_name in TEAM_DATA:
    sport = next((s for s in sports if s.name in sport_name), sports[0])
    Team.objects.get_or_create(
        school=school, name=name, sport=sport,
        defaults=dict(gender=gender, coach=choice(teachers) if teachers else None, is_active=True),
    )
teams = list(Team.objects.filter(school=school))
print(f"  Created {len(teams)} teams")

# Team members
for team in teams[:3]:
    for s in sample(students, min(len(students), team.sport.max_players // 2)):
        TeamMember.objects.get_or_create(team=team, student=s, defaults=dict(role=choice(["member", "vice_captain", "captain"])))

# Events
event_statuses = ["scheduled", "ongoing", "completed", "cancelled"]
for i in range(10):
    team = choice(teams)
    SportEvent.objects.get_or_create(
        school=school, title=f"{team.sport.name} Match #{i+1}",
        defaults=dict(
            sport=team.sport, team=team, opponent=f"Opponent School {i+1}",
            event_date=datetime.now() + timedelta(days=randint(-30, 60)),
            status=choice(event_statuses), home_score=str(randint(0, 100)),
            opponent_score=str(randint(0, 100)),
        ),
    )

# Achievements
for i in range(8):
    student_obj = choice(students) if students else None
    SportAchievement.objects.get_or_create(
        school=school, title=f"Achievement #{i+1}",
        defaults=dict(
            student=student_obj,
            position=choice(["1st Place", "2nd Place", "3rd Place", "Gold Medal", "Silver Medal"]),
            level=choice(["School", "District", "State", "National"]),
            awarded_date=date.today() - timedelta(days=randint(1, 365)),
        ),
    )
print(f"  Created events and achievements")

# ─────────────────────────────────────────────────────────────────────────────
# 2. HEALTH / CLINIC
# ─────────────────────────────────────────────────────────────────────────────
print("\n=== HEALTH & CLINIC ===")
from services.health_clinic.models import HealthRecord, NurseVisit, Immunization, MedicationLog

for student in students[:20]:
    HealthRecord.objects.get_or_create(
        school=school, student=student,
        defaults=dict(
            blood_type=choice(["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]),
            allergies=choice(["Pollen, Dust", "Peanuts", "None", "Latex", "Sulfa Drugs"]),
            chronic_conditions=choice(["Asthma", "None", "None", "Diabetes", "None"]),
            emergency_contact_name=choice(["Mom", "Dad", "Guardian"]),
            emergency_contact_phone=choice(["+1-555-0100", "+1-555-0200", "+1-555-0300"]),
        ),
    )

VISIT_REASONS = ["Fever", "Headache", "Stomach ache", "Minor injury", "Allergy", "Fatigue"]
for _ in range(25):
    student = choice(students)
    NurseVisit.objects.create(
        school=school, student=student,
        visit_type=choice(["sick", "injury", "medication", "checkup", "followup", "other"]),
        symptoms=choice(VISIT_REASONS),
        diagnosis=choice(["Viral infection", "No diagnosis", "Strain", "Allergic reaction"]),
        treatment=choice(["Rest", "Medication given", "Ice pack", "Referred to doctor"]),
        follow_up_date=date.today() + timedelta(days=randint(3, 14)) if choice([True, False]) else None,
        status=choice(["treated", "referred", "medication_given", "observation"]),
    )

VACCINES = ["Hepatitis B", "DTaP", "Polio", "MMR", "Varicella", "HPV", "Meningococcal", "Tdap"]
for student in students[:15]:
    for v in sample(VACCINES, randint(2, 4)):
        Immunization.objects.get_or_create(
            student=student, vaccine_name=v, dose_number=1,
            defaults=dict(date_administered=date.today() - timedelta(days=randint(30, 730))),
        )

print(f"  Created {HealthRecord.objects.count()} records, {NurseVisit.objects.count()} visits, {Immunization.objects.count()} immunizations")

# ─────────────────────────────────────────────────────────────────────────────
# 3. ALUMNI MANAGEMENT
# ─────────────────────────────────────────────────────────────────────────────
print("\n=== ALUMNI MANAGEMENT ===")
from services.alumni.models import AlumniProfile, AlumniEvent, AlumniDonation, AlumniChapter

for student in students[:10]:
    user = student.user
    AlumniProfile.objects.get_or_create(
        school=school, user=user,
        defaults=dict(
            graduation_year=current_year - randint(1, 15),
            occupation=choice(["Engineer", "Doctor", "Teacher", "Business Owner", "Lawyer", "Designer"]),
            employer=choice(["Tech Corp", "City Hospital", "Global School", "Startup Inc", "Law Firm"]),
            employment_status=choice(["employed", "self_employed", "student"]),
            city=choice(["New York", "London", "San Francisco", "Toronto", "Sydney"]),
            country=choice(["USA", "UK", "Canada", "Australia"]),
        ),
    )

for i in range(5):
    AlumniEvent.objects.get_or_create(
        school=school,
        title=choice(["Annual Homecoming", "Alumni Networking Night", "Career Fair",
                       "Class Reunion", "Fundraising Gala"]),
        defaults=dict(
            event_date=datetime.now() + timedelta(days=randint(1, 180)),
            location=school.name,
            status=choice(["draft", "published", "completed"]),
            fee_amount=Decimal(str(randint(0, 5000) / 100)),
        ),
    )

for i in range(6):
    profile = choice(list(AlumniProfile.objects.filter(school=school)))
    AlumniDonation.objects.create(
        school=school, alumni=profile,
        amount=Decimal(str(uniform(50, 10000))),
        fund_type=choice(["general", "scholarship", "infrastructure", "sports", "library"]),
        donation_date=date.today() - timedelta(days=randint(1, 365)),
        is_recurring=choice([True, False]),
    )

for city in ["New York", "London", "Dubai", "Singapore"]:
    AlumniChapter.objects.get_or_create(
        school=school, name=f"{city} Chapter",
        defaults=dict(city=city, country=choice(["USA", "UK", "UAE", "Singapore"]), is_active=True),
    )

print(f"  Created {AlumniProfile.objects.count()} profiles, {AlumniEvent.objects.count()} events, "
      f"{AlumniDonation.objects.count()} donations, {AlumniChapter.objects.count()} chapters")

# ─────────────────────────────────────────────────────────────────────────────
# 4. CAFETERIA / MEAL MANAGEMENT
# ─────────────────────────────────────────────────────────────────────────────
print("\n=== CAFETERIA & MEALS ===")
from services.cafeteria.models import MealMenu, MealPlan, MealBooking, DietaryRestriction

meal_items_map = {
    "breakfast": "Oatmeal, Eggs, Toast, Fruit, Yogurt, Cereal, Pancakes",
    "lunch": "Rice, Chicken, Vegetables, Salad, Pasta, Soup, Bread",
    "dinner": "Stew, Fish, Potatoes, Vegetables, Noodles, Curry, Rice",
    "snack": "Cookies, Fruit, Juice, Crackers, Yogurt, Nuts",
}

for i in range(15):
    day = date.today() + timedelta(days=i)
    for mt in ["breakfast", "lunch", "dinner"]:
        MealMenu.objects.get_or_create(
            school=school, date=day, meal_type=mt,
            defaults=dict(
                name=f"{day.strftime('%a')} {mt.title()}",
                items=meal_items_map[mt],
                price=Decimal(str(randint(150, 500) / 100)),
                is_vegetarian=choice([True, False]),
                is_vegan=choice([True, False]),
                is_gluten_free=choice([True, False]),
            ),
        )

for name, price, days, meals in [
    ("Basic Plan", 99.99, 30, "lunch"),
    ("Standard Plan", 149.99, 30, "breakfast,lunch"),
    ("Premium Plan", 199.99, 30, "breakfast,lunch,dinner"),
    ("Weekend Plan", 59.99, 7, "breakfast,lunch,dinner"),
]:
    MealPlan.objects.get_or_create(
        school=school, name=name,
        defaults=dict(
            description=f"Demo meal plan - {name}",
            price_per_period=Decimal(str(price)),
            period_days=days,
            meals_included=meals,
            is_active=True,
        ),
    )

for student in students[:8]:
    DietaryRestriction.objects.get_or_create(
        user=student.user,
        restriction_type=choice(["Vegetarian", "Vegan", "Gluten-Free", "Nut Allergy", "Lactose Intolerant"]),
        defaults=dict(severity=choice(["Mild", "Moderate", "Severe"])),
    )

menus = list(MealMenu.objects.filter(school=school))
for student in students[:5]:
    if menus:
        MealBooking.objects.get_or_create(
            user=student.user, menu=choice(menus),
            defaults=dict(
                school=school, meal_type=choice(["breakfast", "lunch", "dinner"]),
                status=choice(["confirmed", "attended"]),
            ),
        )

print(f"  Created {MealMenu.objects.count()} menus, {MealPlan.objects.count()} plans, "
      f"{DietaryRestriction.objects.count()} restrictions, {MealBooking.objects.count()} bookings")

# ─────────────────────────────────────────────────────────────────────────────
# 5. ADMISSIONS / ENROLLMENT
# ─────────────────────────────────────────────────────────────────────────────
print("\n=== ADMISSIONS & ENROLLMENT ===")
from services.admissions.models import EnrollmentIntake, Application, ApplicationReview

for name, status in [
    ("Fall 2026 Intake", "open"),
    ("Spring 2027 Intake", "upcoming"),
    ("Summer 2026 Intake", "closed"),
]:
    EnrollmentIntake.objects.get_or_create(
        school=school, name=name,
        defaults=dict(
            academic_year=f"{current_year}-{current_year+1}",
            application_start=date.today() - timedelta(days=60),
            application_end=date.today() + timedelta(days=90),
            status=status,
            max_applications=200,
        ),
    )

intakes = list(EnrollmentIntake.objects.filter(school=school))
for i in range(5):
    first = choice(["James", "Mary", "John", "Patricia", "Robert", "Jennifer",
                     "Michael", "Linda", "David", "Barbara"])
    last = choice(["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"])
    intake = choice(intakes)
    app_num = f"APP-{uuid.uuid4().hex[:8].upper()}"
    Application.objects.get_or_create(
        school=school, first_name=first, last_name=last,
        email=f"{first.lower()}.{last.lower()}{i}@example.com",
        defaults=dict(
            application_number=app_num,
            phone=f"+1-555-{randint(1000,9999)}",
            applying_for_grade=str(randint(1, 12)),
            intake=intake,
            date_of_birth=date(2008 - randint(0, 4), randint(1, 12), randint(1, 28)),
            gender=choice(["male", "female"]),
            status=choice(["draft", "submitted", "under_review", "accepted", "rejected"]),
        ),
    )

apps = list(Application.objects.filter(school=school))
for app in apps[:3]:
    ApplicationReview.objects.get_or_create(
        application=app, reviewer=choice(teachers) if teachers else admin,
        defaults=dict(
            score=randint(50, 100),
            recommendation=choice(["Strongly Recommend", "Recommend", "Consider", "Not Recommended"]),
            notes=f"Demo review for {app.first_name} {app.last_name}",
        ),
    )

print(f"  Created {len(intakes)} intakes, {len(apps)} applications, {ApplicationReview.objects.count()} reviews")

# ─────────────────────────────────────────────────────────────────────────────
# 6. HOSTEL / ACCOMMODATION
# ─────────────────────────────────────────────────────────────────────────────
print("\n=== HOSTEL & ACCOMMODATION ===")
from services.hostel.models import Hostel, HostelRoom, HostelAllocation, HostelFee, HostelVisitor

for name, gender, amenities in [
    ("Sunrise Hall", "male", "WiFi, Laundry, Common Room, Study Area"),
    ("Moonlight Hall", "female", "WiFi, Laundry, Common Room, Kitchen"),
    ("Unity Hostel", "coed", "WiFi, Laundry, Gym, Common Room, Cafeteria"),
]:
    hostel, created = Hostel.objects.get_or_create(
        school=school, name=name,
        defaults=dict(
            gender=gender,
            warden=choice(teachers) if teachers else None,
            amenities=amenities, status="active",
            total_floors=3, notes=f"Demo hostel: {name}",
        ),
    )
    if created:
        for floor in range(1, 4):
            for room_num in range(1, 6):
                HostelRoom.objects.get_or_create(
                    hostel=hostel,
                    room_number=f"{floor}{room_num:02d}",
                    defaults=dict(
                        floor=floor,
                        room_type=choice(["single", "double", "dormitory"]),
                        capacity=randint(1, 4),
                        monthly_fee=Decimal(str(randint(5000, 20000) / 100)),
                        has_ac=choice([True, False]),
                        is_furnished=choice([True, False]),
                    ),
                )

rooms = list(HostelRoom.objects.filter(hostel__school=school))
for i, student in enumerate(students[:6]):
    if i < len(rooms):
        HostelAllocation.objects.get_or_create(
            room=rooms[i], student=student, check_in_date=date.today() - timedelta(days=randint(30, 180)),
            defaults=dict(status="active", fee_amount=Decimal(str(randint(5000, 15000) / 100)), allocated_by=admin),
        )

for hostel in list(Hostel.objects.filter(school=school)):
    for cycle in ["monthly", "quarterly", "annual"]:
        HostelFee.objects.create(
            school=school, hostel=hostel, name=f"{hostel.name} {cycle.title()} Fee",
            billing_cycle=cycle,
            amount=Decimal(str(randint(5000, 30000) / 100)),
            includes_meals=choice([True, False]),
            includes_laundry=True,
            includes_wifi=True,
        )

print(f"  Created {Hostel.objects.count()} hostels, {HostelRoom.objects.count()} rooms, "
      f"{HostelAllocation.objects.count()} allocations")

# ─────────────────────────────────────────────────────────────────────────────
# 7. TRANSPORTATION
# ─────────────────────────────────────────────────────────────────────────────
print("\n=== TRANSPORTATION ===")
from services.transportation.models import Vehicle, Driver, Route, RouteStop

for i, (name, plate, capacity) in enumerate([
    ("Bus #1", "ABC-1234", 40),
    ("Bus #2", "DEF-5678", 36),
    ("Bus #3", "GHI-9012", 30),
    ("Mini Bus #1", "JKL-3456", 16),
], 1):
    Vehicle.objects.get_or_create(
        school=school, plate_number=plate,
        defaults=dict(
            vehicle_type=choice(["bus", "mini_bus", "van"]),
            model_name=f"Demo Model {2020 + i}",
            capacity=capacity,
            is_active=True,
        ),
    )

vehicles = list(Vehicle.objects.filter(school=school))
# Create drivers for the vehicles
for i, vehicle in enumerate(vehicles):
    name = f"Driver {vehicle.plate_number}"
    Driver.objects.get_or_create(
        school=school, full_name=name,
        defaults=dict(phone_number=f"+1-555-{randint(1000,9999)}", status="active"),
    )
drivers = list(Driver.objects.filter(school=school))

for name in ["Morning Route A", "Evening Route A", "Morning Route B"]:
    vehicle = choice(vehicles)
    driver = choice(drivers) if drivers else None
    Route.objects.get_or_create(
        school=school, name=name,
        defaults=dict(
            vehicle=vehicle, driver=driver,
            origin=choice(["Bus Depot", "City Center", "Railway Station"]),
            destination=school.name,
            estimated_duration_minutes=randint(15, 45),
            operating_days="monday,tuesday,wednesday,thursday,friday",
            description=f"Demo route: {name}",
            is_active=True,
        ),
    )

routes = list(Route.objects.filter(school=school))
for route in routes:
    for stop_i, area in enumerate(["Central Park", "Market Square", "Hospital", "Library", "Sports Complex"][:randint(3, 5)]):
        RouteStop.objects.get_or_create(
            route=route, stop_order=stop_i + 1,
            defaults=dict(
                name=area,
                pickup_time=f"{7 + stop_i * 10 // 60:02d}:{(stop_i * 10) % 60:02d}:00" if "Morning" in route.name else None,
                dropoff_time=None if "Morning" in route.name else f"{15 + stop_i * 10 // 60:02d}:{(stop_i * 10) % 60:02d}:00",
                stop_type="both",
                is_active=True,
            ),
        )

print(f"  Created {Vehicle.objects.count()} vehicles, {Driver.objects.count()} drivers, "
      f"{Route.objects.count()} routes, {RouteStop.objects.count()} stops")

# ─────────────────────────────────────────────────────────────────────────────
# 8. INVENTORY / STORE MANAGEMENT
# ─────────────────────────────────────────────────────────────────────────────
print("\n=== INVENTORY & STORE ===")
from services.inventory.models import Category, Supplier, InventoryItem, StockMovement, PurchaseOrder, PurchaseOrderItem

for name, desc in [
    ("Stationery", "Pens, paper, notebooks"),
    ("Uniforms", "School uniforms and PE kits"),
    ("Sports Equipment", "Balls, nets, and sports gear"),
    ("IT Equipment", "Computers, projectors, and accessories"),
    ("Furniture", "Desks, chairs, and storage"),
    ("Cleaning", "Cleaning supplies and hygiene products"),
    ("Kitchen", "Cafeteria utensils and equipment"),
    ("Library", "Books and educational materials"),
]:
    Category.objects.get_or_create(school=school, name=name, defaults=dict(description=desc))
categories = list(Category.objects.filter(school=school))

for name, email, phone in [
    ("OfficeMax Supplies", "contact@officemax.com", "+1-555-1000"),
    ("School Uniforms Inc", "orders@uniforms.com", "+1-555-2000"),
    ("Sports Direct Edu", "sales@sportsdirect.com", "+1-555-3000"),
    ("TechEd Solutions", "info@teched.com", "+1-555-4000"),
]:
    Supplier.objects.get_or_create(
        school=school, name=name,
        defaults=dict(contact_person="Sales Team", email=email, phone=phone, status="active"),
    )
suppliers = list(Supplier.objects.filter(school=school))

ITEMS = [
    ("Box of Pens (50)", "STN-001", "Stationery", 5.99, 200, 20, 500),
    ("Exercise Book (A4)", "STN-002", "Stationery", 2.50, 500, 50, 1000),
    ("School Blazer", "UNI-001", "Uniforms", 45.00, 100, 10, 300),
    ("PE T-Shirt", "UNI-002", "Uniforms", 12.00, 150, 20, 400),
    ("Football (Size 5)", "SPT-001", "Sports Equipment", 25.00, 30, 5, 60),
    ("Basketball", "SPT-002", "Sports Equipment", 30.00, 20, 5, 40),
    ("Laptop Charger", "IT-001", "IT Equipment", 35.00, 15, 5, 30),
    ("Projector Bulb", "IT-002", "IT Equipment", 120.00, 8, 2, 20),
    ("Student Desk", "FRN-001", "Furniture", 85.00, 50, 10, 100),
    ("Chair (Stackable)", "FRN-002", "Furniture", 45.00, 80, 20, 200),
    ("Disinfectant (5L)", "CLN-001", "Cleaning", 15.00, 40, 10, 80),
    ("Hand Soap (Case)", "CLN-002", "Cleaning", 12.00, 60, 15, 120),
    ("Textbook - Math", "LIB-001", "Library", 35.00, 100, 20, 200),
    ("Textbook - Science", "LIB-002", "Library", 38.00, 100, 20, 200),
]

for name, sku, cat_name, price, stock, min_stock, max_stock in ITEMS:
    cat = next(c for c in categories if c.name == cat_name)
    supplier = choice(suppliers)
    InventoryItem.objects.get_or_create(
        school=school, sku=sku,
        defaults=dict(
            name=name, category=cat, supplier=supplier,
            unit_price=Decimal(str(price)),
            current_stock=stock,
            minimum_stock=min_stock,
            maximum_stock=max_stock,
            unit="piece",
            is_active=True,
        ),
    )

items = list(InventoryItem.objects.filter(school=school))
for item in items[:5]:
    StockMovement.objects.create(
        item=item,
        movement_type="purchase",
        quantity=randint(10, 50),
        unit_price=item.unit_price,
        total_amount=item.unit_price * randint(10, 50),
        reference_number="PO-DEMO-001",
        notes="Demo stock purchase",
    )

# Purchase Orders
for i in range(3):
    supplier = choice(suppliers)
    po = PurchaseOrder.objects.create(
        school=school, supplier=supplier,
        order_number=f"PO-DEMO-{uuid.uuid4().hex[:6].upper()}",
        order_date=date.today() - timedelta(days=randint(1, 30)),
        status=choice(["draft", "submitted", "confirmed", "received"]),
        notes=f"Demo purchase order #{i+1}",
        subtotal=Decimal("0"),
        total_amount=Decimal("0"),
    )
    po_total = Decimal("0")
    for item in sample(items, min(3, len(items))):
        qty = randint(5, 20)
        total = item.unit_price * qty
        po_total += total
        PurchaseOrderItem.objects.create(
            purchase_order=po, item=item, quantity_ordered=qty,
            quantity_received=randint(0, qty) if po.status in ["received", "confirmed"] else 0,
            unit_price=item.unit_price,
            total_price=total,
        )
    po.subtotal = po_total
    po.total_amount = po_total
    po.save(update_fields=["subtotal", "total_amount"])

print(f"  Created {Category.objects.count()} categories, {Supplier.objects.count()} suppliers, "
      f"{len(items)} items, {StockMovement.objects.count()} stock movements, "
      f"{PurchaseOrder.objects.count()} purchase orders")

print("\n" + "=" * 60)
print("Demo data seeded successfully for all 8 modules!")
print("=" * 60)
