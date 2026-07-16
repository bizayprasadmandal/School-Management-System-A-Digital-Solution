"""Tests for Cafeteria Service — MealMenu, MealPlan, MealBooking, DietaryRestriction."""

import pytest
from datetime import date
from decimal import Decimal
from rest_framework import status
from rest_framework.test import APIClient
from tests.url_helpers import API_PREFIX

CAFETERIA_MENUS = f"{API_PREFIX}/cafeteria/menus/"
CAFETERIA_PLANS = f"{API_PREFIX}/cafeteria/plans/"
CAFETERIA_BOOKINGS = f"{API_PREFIX}/cafeteria/bookings/"
CAFETERIA_RESTRICTIONS = f"{API_PREFIX}/cafeteria/restrictions/"


@pytest.fixture
def school(db):
    from tests.factories import SchoolFactory
    return SchoolFactory()


@pytest.fixture
def admin(db, school):
    from tests.factories import AdminUserFactory
    return AdminUserFactory(school=school)


@pytest.fixture
def student_user(db, school):
    from tests.factories import StudentUserFactory
    return StudentUserFactory(school=school)


@pytest.fixture
def admin_client(db, admin):
    c = APIClient()
    c.force_authenticate(user=admin)
    return c


@pytest.fixture
def student_client(db, student_user):
    c = APIClient()
    c.force_authenticate(user=student_user)
    return c


@pytest.mark.django_db
class TestMealMenus:

    def test_admin_can_create_menu(self, admin_client, school):
        payload = {
            "name": "Monday Lunch", "meal_type": "lunch",
            "date": date.today().isoformat(),
            "items": "Rice, Chicken, Vegetables",
            "price": "5.00",
        }
        r = admin_client.post(CAFETERIA_MENUS, payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        assert r.data["meal_type"] == "lunch"

    def test_list_menus(self, admin_client, school):
        from services.cafeteria.models import MealMenu
        MealMenu.objects.create(
            school=school, name="Tuesday Breakfast", meal_type="breakfast",
            date=date.today(), items="Pancakes, Eggs", price=Decimal("3.50"),
        )
        r = admin_client.get(CAFETERIA_MENUS)
        assert r.status_code == status.HTTP_200_OK
        assert r.data["count"] >= 1

    def test_student_cannot_create_menu(self, student_client):
        payload = {"name": "Test", "meal_type": "lunch", "date": "2025-01-01"}
        r = student_client.post(CAFETERIA_MENUS, payload, format="json")
        assert r.status_code == status.HTTP_403_FORBIDDEN

    def test_filter_by_meal_type(self, admin_client, school):
        from services.cafeteria.models import MealMenu
        MealMenu.objects.create(
            school=school, name="Snack", meal_type="snack",
            date=date.today(), items="Fruit", price=Decimal("2.00"),
        )
        r = admin_client.get(f"{CAFETERIA_MENUS}?meal_type=snack")
        for m in r.data["results"]:
            assert m["meal_type"] == "snack"


@pytest.mark.django_db
class TestMealPlans:

    def test_create_meal_plan(self, admin_client, school):
        from tests.factories import StudentFactory
        pupil = StudentFactory(school=school)
        payload = {
            "student": pupil.id,
            "plan_type": "weekly",
            "start_date": date.today().isoformat(),
            "total_cost": "25.00",
        }
        r = admin_client.post(CAFETERIA_PLANS, payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED

    def test_student_sees_own_plan(self, student_client, school, student_user):
        from tests.factories import StudentFactory
        from services.cafeteria.models import MealPlan
        pupil = StudentFactory(user=student_user, school=school)
        MealPlan.objects.create(
            school=school, student=pupil,
            plan_type="monthly", start_date=date.today(),
            total_cost=Decimal("80.00"),
        )
        r = student_client.get(CAFETERIA_PLANS)
        assert r.status_code == status.HTTP_200_OK
        assert len(r.data["results"]) >= 1


@pytest.mark.django_db
class TestMealBookings:

    def test_create_booking(self, admin_client, school):
        from tests.factories import StudentFactory
        pupil = StudentFactory(school=school)
        payload = {
            "student": pupil.id,
            "date": date.today().isoformat(),
            "meal_type": "lunch",
        }
        r = admin_client.post(CAFETERIA_BOOKINGS, payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED

    def test_duplicate_booking_rejected(self, admin_client, school):
        from tests.factories import StudentFactory
        pupil = StudentFactory(school=school)
        payload = {
            "student": pupil.id,
            "date": date.today().isoformat(),
            "meal_type": "lunch",
        }
        admin_client.post(CAFETERIA_BOOKINGS, payload, format="json")
        r = admin_client.post(CAFETERIA_BOOKINGS, payload, format="json")
        assert r.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestDietaryRestrictions:

    def test_create_restriction(self, admin_client, school):
        from tests.factories import StudentFactory
        pupil = StudentFactory(school=school)
        payload = {
            "student": pupil.id,
            "allergy": "Peanuts",
            "dietary_type": "vegetarian",
            "notes": "Severe allergic reaction",
        }
        r = admin_client.post(CAFETERIA_RESTRICTIONS, payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED

    def test_list_restrictions(self, admin_client, school):
        from tests.factories import StudentFactory
        from services.cafeteria.models import DietaryRestriction
        pupil = StudentFactory(school=school)
        DietaryRestriction.objects.create(
            school=school, student=pupil,
            allergy="Gluten", dietary_type="gluten_free",
        )
        r = admin_client.get(CAFETERIA_RESTRICTIONS)
        assert r.status_code == status.HTTP_200_OK
        assert r.data["count"] >= 1
