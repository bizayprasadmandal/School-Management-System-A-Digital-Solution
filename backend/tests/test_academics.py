"""Tests for Academics Service — Subjects, TeacherAssignments, TeacherProfiles, LessonPlans."""

import pytest
from rest_framework import status
from rest_framework.test import APIClient
from tests.url_helpers import (
    ACADEMICS_SUBJECTS, ACADEMICS_ASSIGNMENTS,
    ACADEMICS_MY_ASSIGNMENTS, ACADEMICS_LESSON_PLANS,
    ACADEMICS_TEACHER_PROFILES,
)


# ─── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def school(db):
    from tests.factories import SchoolFactory
    return SchoolFactory()


@pytest.fixture
def admin_user(db, school):
    from tests.factories import AdminUserFactory
    return AdminUserFactory(school=school)


@pytest.fixture
def teacher_user(db, school):
    from tests.factories import TeacherUserFactory
    return TeacherUserFactory(school=school)


@pytest.fixture
def student_user(db, school):
    from tests.factories import StudentUserFactory
    return StudentUserFactory(school=school)


@pytest.fixture
def academic_year(db, school):
    from tests.factories import AcademicYearFactory
    return AcademicYearFactory(school=school)


@pytest.fixture
def grade(db, school):
    from tests.factories import GradeFactory
    return GradeFactory(school=school, level=5)


@pytest.fixture
def classroom(db, school, grade, academic_year, teacher_user):
    from tests.factories import ClassroomFactory
    return ClassroomFactory(
        school=school, grade=grade, academic_year=academic_year,
        class_teacher=teacher_user,
    )


@pytest.fixture
def subject(db, school, grade):
    from tests.factories import SubjectFactory
    return SubjectFactory(school=school, grade=grade)


@pytest.fixture
def teacher_assignment(db, teacher_user, subject, classroom, academic_year):
    from tests.factories import TeacherAssignmentFactory
    return TeacherAssignmentFactory(
        teacher=teacher_user, subject=subject,
        classroom=classroom, academic_year=academic_year,
    )


@pytest.fixture
def admin_auth_client(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def teacher_auth_client(api_client, teacher_user):
    api_client.force_authenticate(user=teacher_user)
    return api_client


@pytest.fixture
def student_auth_client(api_client, student_user):
    api_client.force_authenticate(user=student_user)
    return api_client


# ─── Subject Tests ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestSubjects:

    def test_admin_can_create_subject(self, admin_auth_client, school, grade):
        payload = {
            "name": "Physics", "code": "PHY101",
            "grade": grade.id, "max_marks": 100, "pass_marks": 40,
        }
        response = admin_auth_client.post(ACADEMICS_SUBJECTS, payload, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["code"] == "PHY101"

    def test_teacher_cannot_create_subject(self, teacher_auth_client, grade):
        payload = {"name": "Chemistry", "code": "CHM101", "grade": grade.id}
        response = teacher_auth_client.post(ACADEMICS_SUBJECTS, payload, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_student_can_list_subjects(self, student_auth_client, subject):
        response = student_auth_client.get(ACADEMICS_SUBJECTS)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] >= 1

    def test_admin_can_update_subject(self, admin_auth_client, subject):
        response = admin_auth_client.patch(
            f"{ACADEMICS_SUBJECTS}{subject.id}/",
            {"name": "Advanced Physics"}, format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Advanced Physics"

    def test_admin_can_delete_subject(self, admin_auth_client, subject):
        response = admin_auth_client.delete(f"{ACADEMICS_SUBJECTS}{subject.id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_subject_filter_by_grade(self, admin_auth_client, subject):
        response = admin_auth_client.get(f"{ACADEMICS_SUBJECTS}?grade={subject.grade.id}")
        assert response.status_code == status.HTTP_200_OK
        for s in response.data["results"]:
            assert s["grade"] == subject.grade.id

    def test_subject_search_by_name(self, admin_auth_client, subject):
        response = admin_auth_client.get(f"{ACADEMICS_SUBJECTS}?search={subject.name[:4]}")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] >= 1

    def test_tenant_isolation_subject(self, db):
        """Users from School A cannot see School B's subjects."""
        from tests.factories import SchoolFactory, AdminUserFactory, GradeFactory, SubjectFactory
        school_a = SchoolFactory(code="ISOA")
        school_b = SchoolFactory(code="ISOB")
        admin_a = AdminUserFactory(school=school_a)
        grade_b = GradeFactory(school=school_b)
        SubjectFactory(school=school_b, grade=grade_b)

        client = APIClient()
        client.force_authenticate(user=admin_a)
        response = client.get(ACADEMICS_SUBJECTS)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 0


# ─── TeacherAssignment Tests ──────────────────────────────────────────────────

@pytest.mark.django_db
class TestTeacherAssignments:

    def test_admin_can_create_assignment(self, admin_auth_client, teacher_user, subject, classroom, academic_year):
        payload = {
            "teacher": teacher_user.id, "subject": subject.id,
            "classroom": classroom.id, "academic_year": academic_year.id,
        }
        response = admin_auth_client.post(ACADEMICS_ASSIGNMENTS, payload, format="json")
        assert response.status_code == status.HTTP_201_CREATED

    def test_teacher_cannot_create_assignment(self, teacher_auth_client, subject, classroom, academic_year):
        payload = {
            "teacher": 9999, "subject": subject.id,
            "classroom": classroom.id, "academic_year": academic_year.id,
        }
        response = teacher_auth_client.post(ACADEMICS_ASSIGNMENTS, payload, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_teacher_my_assignments(self, teacher_auth_client, teacher_assignment):
        response = teacher_auth_client.get(ACADEMICS_MY_ASSIGNMENTS)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
        assert response.data[0]["teacher"] == teacher_assignment.teacher.id

    def test_other_teacher_my_assignments_empty(self, db, school):
        """A different teacher sees no assignments from another teacher."""
        from tests.factories import TeacherAssignmentFactory, TeacherUserFactory
        other_teacher = TeacherUserFactory(school=school)
        client = APIClient()
        client.force_authenticate(user=other_teacher)
        response = client.get(ACADEMICS_MY_ASSIGNMENTS)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

    def test_assignment_filter_by_subject(self, admin_auth_client, teacher_assignment):
        response = admin_auth_client.get(
            f"{ACADEMICS_ASSIGNMENTS}?subject={teacher_assignment.subject.id}"
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] >= 1

    def test_admin_can_delete_assignment(self, admin_auth_client, teacher_assignment):
        response = admin_auth_client.delete(
            f"{ACADEMICS_ASSIGNMENTS}{teacher_assignment.id}/"
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT


# ─── TeacherProfile Tests ─────────────────────────────────────────────────────

@pytest.mark.django_db
class TestTeacherProfiles:

    def test_list_teacher_profiles(self, admin_auth_client):
        response = admin_auth_client.get(ACADEMICS_TEACHER_PROFILES)
        assert response.status_code == status.HTTP_200_OK

    def test_teacher_profile_search(self, admin_auth_client, teacher_user):
        from tests.factories import TeacherProfileFactory
        TeacherProfileFactory(user=teacher_user, school=teacher_user.school)
        response = admin_auth_client.get(
            f"{ACADEMICS_TEACHER_PROFILES}?search={teacher_user.first_name}"
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] >= 1

    def test_student_can_read_profiles(self, student_auth_client, teacher_user):
        from tests.factories import TeacherProfileFactory
        TeacherProfileFactory(user=teacher_user, school=teacher_user.school)
        response = student_auth_client.get(ACADEMICS_TEACHER_PROFILES)
        assert response.status_code == status.HTTP_200_OK


# ─── LessonPlan Tests ─────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestLessonPlans:

    def test_teacher_can_create_lesson_plan(self, teacher_auth_client, teacher_assignment):
        payload = {
            "assignment": teacher_assignment.id,
            "title": "Introduction to Algebra",
            "topic": "Linear Equations",
            "objectives": "Understand basic equations",
            "content": "Content here",
            "date": "2025-03-10",
            "duration_minutes": 45,
        }
        response = teacher_auth_client.post(ACADEMICS_LESSON_PLANS, payload, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["title"] == "Introduction to Algebra"

    def test_student_cannot_create_lesson_plan(self, student_auth_client, teacher_assignment):
        payload = {
            "assignment": teacher_assignment.id,
            "title": "Test", "topic": "Test",
            "objectives": "Test", "content": "Test",
            "date": "2025-03-10",
        }
        response = student_auth_client.post(ACADEMICS_LESSON_PLANS, payload, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_lesson_plan_list_and_filter(self, teacher_auth_client, teacher_assignment):
        from tests.factories import LessonPlanFactory
        LessonPlanFactory(assignment=teacher_assignment, date="2025-03-10")
        response = teacher_auth_client.get(
            f"{ACADEMICS_LESSON_PLANS}?assignment={teacher_assignment.id}"
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] >= 1

    def test_admin_can_approve_lesson_plan(self, admin_auth_client, teacher_assignment):
        from tests.factories import LessonPlanFactory
        plan = LessonPlanFactory(assignment=teacher_assignment, status="draft")
        response = admin_auth_client.post(f"{ACADEMICS_LESSON_PLANS}{plan.id}/approve/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "approved"

    def test_teacher_cannot_approve_own_plan(self, teacher_auth_client, teacher_assignment):
        from tests.factories import LessonPlanFactory
        plan = LessonPlanFactory(assignment=teacher_assignment, status="draft")
        response = teacher_auth_client.post(f"{ACADEMICS_LESSON_PLANS}{plan.id}/approve/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_lesson_plan_search(self, admin_auth_client, teacher_assignment):
        from tests.factories import LessonPlanFactory
        LessonPlanFactory(assignment=teacher_assignment, title="Quadratic Equations")
        response = admin_auth_client.get(f"{ACADEMICS_LESSON_PLANS}?search=Quadratic")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] >= 1
