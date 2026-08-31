"""
Tests for Academics module — subjects, teacher assignments, lesson plans,
and the new StudentSubjectEnrollment feature.
"""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

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
def admin_auth(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def teacher_user(db, school):
    from tests.factories import TeacherUserFactory

    return TeacherUserFactory(school=school)


@pytest.fixture
def teacher_auth(api_client, teacher_user):
    api_client.force_authenticate(user=teacher_user)
    return api_client


@pytest.fixture
def student_user(db, school):
    from tests.factories import StudentUserFactory

    return StudentUserFactory(school=school)


@pytest.fixture
def student(db, school, student_user):
    from tests.factories import StudentFactory

    return StudentFactory(user=student_user, school=school)


@pytest.fixture
def grade(db, school):
    from tests.factories import GradeFactory

    return GradeFactory(school=school, level=6)


@pytest.fixture
def academic_year(db, school):
    from tests.factories import AcademicYearFactory

    return AcademicYearFactory(school=school)


@pytest.fixture
def classroom(db, school, grade, academic_year):
    from tests.factories import ClassroomFactory

    return ClassroomFactory(school=school, grade=grade, academic_year=academic_year)


@pytest.fixture
def subject(db, school, grade):
    from tests.factories import SubjectFactory

    return SubjectFactory(school=school, grade=grade)


@pytest.fixture
def teacher_assignment(db, teacher_user, subject, classroom, academic_year):
    from tests.factories import TeacherAssignmentFactory

    return TeacherAssignmentFactory(
        teacher=teacher_user, subject=subject, classroom=classroom, academic_year=academic_year
    )


# ─── Subject Tests ────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestSubjectModule:

    def test_list_subjects(self, admin_auth):
        response = admin_auth.get("/api/v1/academics/subjects/")
        assert response.status_code == status.HTTP_200_OK

    def test_create_subject(self, admin_auth, grade):
        response = admin_auth.post(
            "/api/v1/academics/subjects/",
            {
                "name": "Mathematics",
                "code": "MATH101",
                "grade": grade.id,
                "is_core": True,
                "max_marks": 100,
                "pass_marks": 40,
            },
            format="json",
        )
        assert response.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK)


# ─── Teacher Assignment Tests ────────────────────────────────────────────────


@pytest.mark.django_db
class TestTeacherAssignmentModule:

    def test_list_assignments(self, admin_auth):
        response = admin_auth.get("/api/v1/academics/assignments/")
        assert response.status_code == status.HTTP_200_OK

    def test_my_assignments(self, teacher_auth, teacher_assignment):
        response = teacher_auth.get("/api/v1/academics/assignments/my-assignments/")
        assert response.status_code == status.HTTP_200_OK


# ─── Lesson Plan Tests ───────────────────────────────────────────────────────


@pytest.mark.django_db
class TestLessonPlanModule:

    def test_list_lesson_plans(self, admin_auth):
        response = admin_auth.get("/api/v1/academics/lesson-plans/")
        assert response.status_code == status.HTTP_200_OK


# ─── Student-Subject Enrollment Tests ────────────────────────────────────────


@pytest.mark.django_db
class TestStudentSubjectEnrollment:

    def test_list_enrollments(self, admin_auth):
        response = admin_auth.get("/api/v1/academics/student-subject-enrollments/")
        assert response.status_code == status.HTTP_200_OK

    def test_create_enrollment(self, admin_auth, student, subject, academic_year):
        response = admin_auth.post(
            "/api/v1/academics/student-subject-enrollments/",
            {
                "student": str(student.id),
                "subject": subject.id,
                "academic_year": academic_year.id,
            },
            format="json",
        )
        assert response.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK)
        assert response.data["status"] == "active"

    def test_create_enrollment_duplicate_fails(self, admin_auth, student, subject, academic_year):
        # Create first enrollment
        admin_auth.post(
            "/api/v1/academics/student-subject-enrollments/",
            {
                "student": str(student.id),
                "subject": subject.id,
                "academic_year": academic_year.id,
            },
            format="json",
        )
        # Try duplicate
        response = admin_auth.post(
            "/api/v1/academics/student-subject-enrollments/",
            {
                "student": str(student.id),
                "subject": subject.id,
                "academic_year": academic_year.id,
            },
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_bulk_enroll(self, admin_auth, subject, academic_year, student, school):
        from tests.factories import StudentFactory

        student2 = StudentFactory(school=school)
        response = admin_auth.post(
            "/api/v1/academics/student-subject-enrollments/bulk-enroll/",
            {
                "subject": subject.id,
                "academic_year": academic_year.id,
                "student_ids": [str(student.id), str(student2.id)],
            },
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["enrolled"] == 2

    def test_bulk_enroll_missing_fields(self, admin_auth):
        response = admin_auth.post(
            "/api/v1/academics/student-subject-enrollments/bulk-enroll/",
            {
                "subject": 1,
            },
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_my_subjects_endpoint(self, api_client, student_user, student, subject, academic_year):
        from services.academics.models import StudentSubjectEnrollment

        StudentSubjectEnrollment.objects.create(student=student, subject=subject, academic_year=academic_year)
        api_client.force_authenticate(user=student_user)
        response = api_client.get("/api/v1/academics/student-subject-enrollments/my-subjects/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_subject_students_endpoint(self, admin_auth, student, subject, academic_year):
        from services.academics.models import StudentSubjectEnrollment

        StudentSubjectEnrollment.objects.create(student=student, subject=subject, academic_year=academic_year)
        response = admin_auth.get(f"/api/v1/academics/student-subject-enrollments/subject-students/{subject.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_update_enrollment_status(self, admin_auth, student, subject, academic_year):
        from services.academics.models import StudentSubjectEnrollment

        enrollment = StudentSubjectEnrollment.objects.create(
            student=student, subject=subject, academic_year=academic_year
        )
        response = admin_auth.patch(
            f"/api/v1/academics/student-subject-enrollments/{enrollment.id}/",
            {"status": "dropped"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "dropped"

    def test_delete_enrollment(self, admin_auth, student, subject, academic_year):
        from services.academics.models import StudentSubjectEnrollment

        enrollment = StudentSubjectEnrollment.objects.create(
            student=student, subject=subject, academic_year=academic_year
        )
        response = admin_auth.delete(f"/api/v1/academics/student-subject-enrollments/{enrollment.id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_filter_by_status(self, admin_auth, student, subject, academic_year):
        from services.academics.models import StudentSubjectEnrollment

        StudentSubjectEnrollment.objects.create(
            student=student, subject=subject, academic_year=academic_year, status="active"
        )
        response = admin_auth.get("/api/v1/academics/student-subject-enrollments/?status=active")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1

    def test_student_cannot_create_enrollment(self, api_client, student_user, student, subject, academic_year):
        api_client.force_authenticate(user=student_user)
        response = api_client.post(
            "/api/v1/academics/student-subject-enrollments/",
            {
                "student": str(student.id),
                "subject": subject.id,
                "academic_year": academic_year.id,
            },
            format="json",
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


# ─── Curriculum Standards Tests ──────────────────────────────────────────────


@pytest.mark.django_db
class TestCurriculumStandard:

    def test_list_standards(self, admin_auth):
        response = admin_auth.get("/api/v1/academics/curriculum-standards/")
        assert response.status_code == status.HTTP_200_OK

    def test_create_standard(self, admin_auth, grade):
        response = admin_auth.post(
            "/api/v1/academics/curriculum-standards/",
            {
                "framework": "common_core",
                "code": "CCSS.MATH.8.EE.1",
                "name": "Express and perform operations with radicals",
                "grade": grade.id,
                "domain": "Algebra",
            },
            format="json",
        )
        assert response.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK)

    def test_bulk_create_standards(self, admin_auth, grade):
        response = admin_auth.post(
            "/api/v1/academics/curriculum-standards/bulk-create/",
            {
                "framework": "common_core",
                "standards": [
                    {
                        "code": "CCSS.MATH.8.EE.1",
                        "name": "Express and perform operations with radicals",
                        "grade_id": grade.id,
                        "domain": "Algebra",
                    },
                    {
                        "code": "CCSS.MATH.8.EE.2",
                        "name": "Use square root and cube root symbols",
                        "grade_id": grade.id,
                        "domain": "Algebra",
                    },
                ],
            },
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["created"] == 2

    def test_bulk_create_skips_duplicates(self, admin_auth, grade):
        from tests.factories import CurriculumStandardFactory

        CurriculumStandardFactory(school=admin_auth.handler._view.request.user.school, code="DUP-001")
        response = admin_auth.post(
            "/api/v1/academics/curriculum-standards/bulk-create/",
            {
                "framework": "custom",
                "standards": [
                    {"code": "DUP-001", "name": "Duplicate"},
                    {"code": "NEW-001", "name": "New Standard"},
                ],
            },
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["created"] == 1
        assert response.data["skipped"] == 1

    def test_by_framework_endpoint(self, admin_auth):
        from tests.factories import CurriculumStandardFactory

        school = admin_auth.handler._view.request.user.school
        CurriculumStandardFactory(school=school, framework="common_core", code="CC-01")
        CurriculumStandardFactory(school=school, framework="ngss", code="NGSS-01")
        response = admin_auth.get("/api/v1/academics/curriculum-standards/by-framework/")
        assert response.status_code == status.HTTP_200_OK
        assert "common_core" in response.data
        assert "ngss" in response.data


# ─── Subject-Standard Mapping Tests ─────────────────────────────────────────


@pytest.mark.django_db
class TestSubjectStandardMapping:

    def test_list_mappings(self, admin_auth):
        response = admin_auth.get("/api/v1/academics/subject-standard-mappings/")
        assert response.status_code == status.HTTP_200_OK

    def test_create_mapping(self, admin_auth, subject, academic_year):
        from tests.factories import CurriculumStandardFactory

        school = admin_auth.handler._view.request.user.school
        standard = CurriculumStandardFactory(school=school)
        response = admin_auth.post(
            "/api/v1/academics/subject-standard-mappings/",
            {
                "subject": subject.id,
                "standard": standard.id,
                "academic_year": academic_year.id,
                "coverage_level": "partial",
            },
            format="json",
        )
        assert response.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK)

    def test_bulk_map_standards(self, admin_auth, subject, academic_year):
        from tests.factories import CurriculumStandardFactory

        school = admin_auth.handler._view.request.user.school
        std1 = CurriculumStandardFactory(school=school)
        std2 = CurriculumStandardFactory(school=school)
        response = admin_auth.post(
            "/api/v1/academics/subject-standard-mappings/bulk-map/",
            {
                "subject": subject.id,
                "academic_year": academic_year.id,
                "standard_ids": [std1.id, std2.id],
                "coverage_level": "full",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["mapped"] == 2

    def test_subject_coverage_endpoint(self, admin_auth, subject, academic_year):
        from services.academics.models import SubjectStandardMapping
        from tests.factories import CurriculumStandardFactory

        school = admin_auth.handler._view.request.user.school
        standard = CurriculumStandardFactory(school=school)
        SubjectStandardMapping.objects.create(
            subject=subject, standard=standard, academic_year=academic_year, coverage_level="full"
        )
        response = admin_auth.get(f"/api/v1/academics/subject-standard-mappings/subject-coverage/{subject.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_coverage_report_endpoint(self, admin_auth, subject, academic_year):
        from tests.factories import CurriculumStandardFactory

        school = admin_auth.handler._view.request.user.school
        standard = CurriculumStandardFactory(school=school)
        from services.academics.models import SubjectStandardMapping

        SubjectStandardMapping.objects.create(
            subject=subject, standard=standard, academic_year=academic_year, coverage_level="full"
        )
        response = admin_auth.get(
            f"/api/v1/academics/subject-standard-mappings/coverage-report/?academic_year={academic_year.id}"
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["full_count"] == 1
