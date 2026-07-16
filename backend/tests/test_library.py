"""Tests for Library Service — Book, Checkout."""

import pytest
from datetime import date, timedelta
from rest_framework import status
from rest_framework.test import APIClient
from tests.url_helpers import API_PREFIX

LIBRARY_BOOKS = f"{API_PREFIX}/library/books/"
LIBRARY_CHECKOUTS = f"{API_PREFIX}/library/checkouts/"


@pytest.fixture
def school(db):
    from tests.factories import SchoolFactory
    return SchoolFactory()


@pytest.fixture
def admin(db, school):
    from tests.factories import AdminUserFactory
    return AdminUserFactory(school=school)


@pytest.fixture
def teacher(db, school):
    from tests.factories import TeacherUserFactory
    return TeacherUserFactory(school=school)


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
def teacher_client(db, teacher):
    c = APIClient()
    c.force_authenticate(user=teacher)
    return c


@pytest.fixture
def student_client(db, student_user):
    c = APIClient()
    c.force_authenticate(user=student_user)
    return c


@pytest.fixture
def book(db, school):
    from services.library.models import Book
    return Book.objects.create(
        school=school,
        title="Introduction to Python",
        author="John Smith",
        isbn="978-0-123456-78-9",
        total_copies=5,
        available_copies=5,
    )


@pytest.mark.django_db
class TestBooks:

    def test_admin_can_create_book(self, admin_client, school):
        payload = {
            "title": "Data Structures",
            "author": "Jane Doe",
            "isbn": "978-0-987654-32-1",
            "publisher": "Tech Press",
            "total_copies": 10,
        }
        r = admin_client.post(LIBRARY_BOOKS, payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        assert r.data["title"] == "Data Structures"
        assert r.data["available_copies"] == 10

    def test_teacher_can_create_book(self, teacher_client, school):
        payload = {
            "title": "Algorithms", "author": "Bob Wilson",
            "isbn": "978-0-111111-11-1", "total_copies": 3,
        }
        r = teacher_client.post(LIBRARY_BOOKS, payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED

    def test_student_cannot_create_book(self, student_client):
        payload = {
            "title": "Hack", "author": "Hacker",
            "isbn": "978-0-000000-00-0", "total_copies": 1,
        }
        r = student_client.post(LIBRARY_BOOKS, payload, format="json")
        assert r.status_code == status.HTTP_403_FORBIDDEN

    def test_list_books(self, admin_client, book):
        r = admin_client.get(LIBRARY_BOOKS)
        assert r.status_code == status.HTTP_200_OK
        assert r.data["count"] >= 1

    def test_search_books(self, admin_client, book):
        r = admin_client.get(f"{LIBRARY_BOOKS}?search=Python")
        assert r.status_code == status.HTTP_200_OK
        assert r.data["count"] >= 1

    def test_filter_available_books(self, admin_client, book):
        r = admin_client.get(f"{LIBRARY_BOOKS}?available=true")
        assert r.status_code == status.HTTP_200_OK
        for b in r.data["results"]:
            assert b["available_copies"] > 0

    def test_tenant_isolation_book(self, db):
        from tests.factories import SchoolFactory, AdminUserFactory
        from services.library.models import Book
        school_a = SchoolFactory(code="LIBA")
        school_b = SchoolFactory(code="LIBB")
        admin_a = AdminUserFactory(school=school_a)
        Book.objects.create(
            school=school_b, title="Secret Book",
            author="Author", isbn="978-0-999999-99-9",
            total_copies=1, available_copies=1,
        )
        client = APIClient()
        client.force_authenticate(user=admin_a)
        r = client.get(LIBRARY_BOOKS)
        titles = [b["title"] for b in r.data["results"]]
        assert "Secret Book" not in titles


@pytest.mark.django_db
class TestCheckouts:

    def test_checkout_book(self, admin_client, book):
        from tests.factories import UserFactory
        user = UserFactory(school=book.school)
        payload = {
            "book": book.id,
            "borrower": user.id,
            "due_date": (date.today() + timedelta(days=14)).isoformat(),
        }
        r = admin_client.post(LIBRARY_CHECKOUTS, payload, format="json")
        assert r.status_code == status.HTTP_201_CREATED
        assert r.data["status"] == "active"
        book.refresh_from_db()
        assert book.available_copies == 4

    def test_checkout_unavailable_book(self, admin_client, book):
        book.available_copies = 0
        book.save()
        from tests.factories import UserFactory
        user = UserFactory(school=book.school)
        payload = {
            "book": book.id, "borrower": user.id,
            "due_date": (date.today() + timedelta(days=14)).isoformat(),
        }
        r = admin_client.post(LIBRARY_CHECKOUTS, payload, format="json")
        assert r.status_code == status.HTTP_400_BAD_REQUEST

    def test_return_book(self, admin_client, book):
        from tests.factories import UserFactory
        from services.library.models import Checkout
        user = UserFactory(school=book.school)
        checkout = Checkout.objects.create(
            book=book, borrower=user,
            checkout_date=date.today(),
            due_date=date.today() + timedelta(days=14),
            status="active",
        )
        r = admin_client.post(f"{LIBRARY_CHECKOUTS}{checkout.id}/return/")
        assert r.status_code == status.HTTP_200_OK
        checkout.refresh_from_db()
        assert checkout.status == "returned"
        assert checkout.return_date is not None
        book.refresh_from_db()
        assert book.available_copies == 5

    def test_list_active_checkouts(self, admin_client, book):
        from tests.factories import UserFactory
        from services.library.models import Checkout
        user = UserFactory(school=book.school)
        Checkout.objects.create(
            book=book, borrower=user,
            checkout_date=date.today(),
            due_date=date.today() + timedelta(days=14),
            status="active",
        )
        r = admin_client.get(f"{LIBRARY_CHECKOUTS}?status=active")
        assert r.status_code == status.HTTP_200_OK
        for c in r.data["results"]:
            assert c["status"] == "active"

    def test_overdue_checkouts(self, admin_client, book):
        from tests.factories import UserFactory
        from services.library.models import Checkout
        user = UserFactory(school=book.school)
        Checkout.objects.create(
            book=book, borrower=user,
            checkout_date=date.today() - timedelta(days=30),
            due_date=date.today() - timedelta(days=16),
            status="active",
        )
        r = admin_client.get(f"{LIBRARY_CHECKOUTS}?overdue=true")
        assert r.status_code == status.HTTP_200_OK
        assert len(r.data["results"]) >= 1
