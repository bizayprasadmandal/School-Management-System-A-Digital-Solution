"""Regression tests for the Classrooms page contract.

The admin Classrooms page filters by grade via ``?grade=<id>`` and renders
``grade_name`` / ``teacher_name`` / ``student_count`` per row. The filter
silently returned the full list until ``filterset_fields`` was wired up, and
the display fields did not exist on the serializer.
"""

import pytest
from rest_framework import status
from rest_framework.test import APIClient
from tests.factories import (
    AdminUserFactory,
    ClassroomFactory,
    EnrollmentFactory,
    GradeFactory,
    SchoolFactory,
    StudentFactory,
    TeacherUserFactory,
)
from tests.url_helpers import CLASSROOMS_LIST

pytestmark = pytest.mark.django_db


@pytest.fixture
def school():
    return SchoolFactory()


@pytest.fixture
def admin(school):
    return AdminUserFactory(school=school)


@pytest.fixture
def api(admin):
    client = APIClient(SERVER_NAME="localhost")
    client.force_authenticate(user=admin)
    return client


def test_grade_filter_narrows_classrooms(api, school):
    grade1 = GradeFactory(school=school, name="Grade 1", level=1)
    grade2 = GradeFactory(school=school, name="Grade 2", level=2)
    ClassroomFactory(school=school, grade=grade1, name="1A")
    ClassroomFactory(school=school, grade=grade1, name="1B")
    ClassroomFactory(school=school, grade=grade2, name="2A")

    response = api.get(CLASSROOMS_LIST, {"grade": grade1.pk})

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 2
    assert all(row["grade"] == grade1.pk for row in response.data["results"])

    # the other grade narrows to its own row
    response = api.get(CLASSROOMS_LIST, {"grade": grade2.pk})
    assert response.data["count"] == 1


def test_unfiltered_list_returns_all_and_display_fields(api, school):
    teacher = TeacherUserFactory(school=school)
    grade = GradeFactory(school=school, name="Grade 5", level=5)
    classroom = ClassroomFactory(school=school, grade=grade, name="5A", class_teacher=teacher)
    student = StudentFactory(school=school)
    EnrollmentFactory(student=student, classroom=classroom, is_active=True)
    EnrollmentFactory(student=StudentFactory(school=school), classroom=classroom, is_active=False)

    response = api.get(CLASSROOMS_LIST)

    assert response.status_code == status.HTTP_200_OK
    row = next(r for r in response.data["results"] if r["id"] == classroom.pk)
    assert row["grade_name"] == "Grade 5"
    assert row["teacher_name"] == teacher.full_name
    # only the active enrollment counts toward the seat usage
    assert row["student_count"] == 1
