"""
Tests for Academics module — subjects, teacher assignments, lesson plans,
and the new StudentSubjectEnrollment feature.
"""

from decimal import Decimal

import pytest
from rest_framework import status
from rest_framework.test import APIClient
from tests.factories import (
    AcademicTranscriptFactory,
    AcademicYearFactory,
    AdminUserFactory,
    ClassroomFactory,
    GradeFactory,
    SchoolFactory,
    StudentFactory,
    StudentUserFactory,
    SubjectFactory,
    TeacherUserFactory,
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


# ─── Syllabus Management Tests ──────────────────────────────────────────────


@pytest.mark.django_db
class TestSyllabus:

    def test_list_syllabi(self, admin_auth):
        response = admin_auth.get("/api/v1/academics/syllabi/")
        assert response.status_code == status.HTTP_200_OK

    def test_create_syllabus(self, teacher_auth, subject, academic_year, teacher_user):
        # Link teacher to subject
        from tests.factories import TeacherAssignmentFactory

        TeacherAssignmentFactory(teacher=teacher_user, subject=subject, academic_year=academic_year)
        response = teacher_auth.post(
            "/api/v1/academics/syllabi/",
            {
                "subject": subject.id,
                "academic_year": academic_year.id,
                "term": "1st",
                "title": "First Term Mathematics",
                "learning_objectives": "Master algebra basics",
                "total_hours": 60,
            },
            format="json",
        )
        assert response.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK)
        assert response.data["status"] == "draft"

    def test_submit_for_review(self, teacher_auth, subject, academic_year, teacher_user):
        from services.academics.models import Syllabus
        from tests.factories import TeacherAssignmentFactory

        TeacherAssignmentFactory(teacher=teacher_user, subject=subject, academic_year=academic_year)
        syllabus = Syllabus.objects.create(
            subject=subject,
            academic_year=academic_year,
            term="1st",
            title="Test Syllabus",
            learning_objectives="Learn things",
            created_by=teacher_user,
        )
        response = teacher_auth.post(f"/api/v1/academics/syllabi/{syllabus.id}/submit-for-review/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "under_review"

    def test_approve_syllabus(self, admin_auth, subject, academic_year):
        from services.academics.models import Syllabus

        admin = admin_auth.handler._view.request.user
        syllabus = Syllabus.objects.create(
            subject=subject,
            academic_year=academic_year,
            term="1st",
            title="Test Syllabus",
            learning_objectives="Learn things",
            status="under_review",
            created_by=admin,
        )
        response = admin_auth.post(f"/api/v1/academics/syllabi/{syllabus.id}/approve/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "approved"

    def test_reject_syllabus(self, admin_auth, subject, academic_year):
        from services.academics.models import Syllabus

        admin = admin_auth.handler._view.request.user
        syllabus = Syllabus.objects.create(
            subject=subject,
            academic_year=academic_year,
            term="1st",
            title="Test Syllabus",
            learning_objectives="Learn things",
            status="under_review",
            created_by=admin,
        )
        response = admin_auth.post(
            f"/api/v1/academics/syllabi/{syllabus.id}/reject/",
            {"reason": "Insufficient detail"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "rejected"

    def test_reject_syllabus_requires_reason(self, admin_auth, subject, academic_year):
        from services.academics.models import Syllabus

        admin = admin_auth.handler._view.request.user
        syllabus = Syllabus.objects.create(
            subject=subject,
            academic_year=academic_year,
            term="1st",
            title="Test Syllabus",
            learning_objectives="Learn things",
            status="under_review",
            created_by=admin,
        )
        response = admin_auth.post(f"/api/v1/academics/syllabi/{syllabus.id}/reject/")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_progress_endpoint(self, teacher_auth, subject, academic_year, teacher_user):
        from services.academics.models import Syllabus, SyllabusTopic
        from tests.factories import TeacherAssignmentFactory

        TeacherAssignmentFactory(teacher=teacher_user, subject=subject, academic_year=academic_year)
        syllabus = Syllabus.objects.create(
            subject=subject,
            academic_year=academic_year,
            term="1st",
            title="Test Syllabus",
            learning_objectives="Learn things",
            total_hours=20,
            created_by=teacher_user,
        )
        SyllabusTopic.objects.create(
            syllabus=syllabus, order=1, title="Topic 1", estimated_hours=10, status="completed"
        )
        SyllabusTopic.objects.create(
            syllabus=syllabus, order=2, title="Topic 2", estimated_hours=10, status="in_progress"
        )
        response = teacher_auth.get(f"/api/v1/academics/syllabi/{syllabus.id}/progress/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["total_topics"] == 2
        assert response.data["completed_topics"] == 1
        assert response.data["progress_percentage"] == 50.0


# ─── Syllabus Topic Tests ──────────────────────────────────────────────────


@pytest.mark.django_db
class TestSyllabusTopic:

    def test_list_topics(self, teacher_auth, subject, academic_year, teacher_user):
        from services.academics.models import Syllabus, SyllabusTopic
        from tests.factories import TeacherAssignmentFactory

        TeacherAssignmentFactory(teacher=teacher_user, subject=subject, academic_year=academic_year)
        syllabus = Syllabus.objects.create(
            subject=subject,
            academic_year=academic_year,
            term="1st",
            title="Test Syllabus",
            learning_objectives="Learn things",
            created_by=teacher_user,
        )
        SyllabusTopic.objects.create(syllabus=syllabus, order=1, title="Topic 1")
        response = teacher_auth.get(f"/api/v1/academics/syllabi/{syllabus.id}/topics/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1

    def test_create_topic(self, teacher_auth, subject, academic_year, teacher_user):
        from services.academics.models import Syllabus
        from tests.factories import TeacherAssignmentFactory

        TeacherAssignmentFactory(teacher=teacher_user, subject=subject, academic_year=academic_year)
        syllabus = Syllabus.objects.create(
            subject=subject,
            academic_year=academic_year,
            term="1st",
            title="Test Syllabus",
            learning_objectives="Learn things",
            created_by=teacher_user,
        )
        response = teacher_auth.post(
            f"/api/v1/academics/syllabi/{syllabus.id}/topics/",
            {
                "order": 1,
                "title": "Algebra Basics",
                "estimated_hours": "4.0",
            },
            format="json",
        )
        assert response.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK)
        assert response.data["status"] == "not_started"

    def test_start_topic(self, teacher_auth, subject, academic_year, teacher_user):
        from services.academics.models import Syllabus, SyllabusTopic
        from tests.factories import TeacherAssignmentFactory

        TeacherAssignmentFactory(teacher=teacher_user, subject=subject, academic_year=academic_year)
        syllabus = Syllabus.objects.create(
            subject=subject,
            academic_year=academic_year,
            term="1st",
            title="Test Syllabus",
            learning_objectives="Learn things",
            created_by=teacher_user,
        )
        topic = SyllabusTopic.objects.create(syllabus=syllabus, order=1, title="Topic 1")
        response = teacher_auth.post(f"/api/v1/academics/syllabi/{syllabus.id}/topics/{topic.id}/start/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "in_progress"
        assert response.data["started_at"] is not None

    def test_complete_topic(self, teacher_auth, subject, academic_year, teacher_user):
        from services.academics.models import Syllabus, SyllabusTopic
        from tests.factories import TeacherAssignmentFactory

        TeacherAssignmentFactory(teacher=teacher_user, subject=subject, academic_year=academic_year)
        syllabus = Syllabus.objects.create(
            subject=subject,
            academic_year=academic_year,
            term="1st",
            title="Test Syllabus",
            learning_objectives="Learn things",
            created_by=teacher_user,
        )
        topic = SyllabusTopic.objects.create(syllabus=syllabus, order=1, title="Topic 1", status="in_progress")
        response = teacher_auth.post(f"/api/v1/academics/syllabi/{syllabus.id}/topics/{topic.id}/complete/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "completed"
        assert response.data["completed_at"] is not None


# ─── Teacher Workload Tests ─────────────────────────────────────────────────


@pytest.mark.django_db
class TestTeacherWorkloadConfig:

    def test_list_workload_config(self, admin_auth):
        response = admin_auth.get("/api/v1/academics/workload-config/")
        assert response.status_code == status.HTTP_200_OK

    def test_create_workload_config(self, admin_auth):
        response = admin_auth.post(
            "/api/v1/academics/workload-config/",
            {
                "max_periods_per_week": 25,
                "max_periods_per_day": 6,
                "max_subjects": 3,
                "max_classes": 4,
                "min_periods_per_week": 15,
                "warning_threshold_pct": 85,
            },
            format="json",
        )
        assert response.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK)

    def test_update_workload_config(self, admin_auth, school):
        from tests.factories import TeacherWorkloadConfigFactory

        config = TeacherWorkloadConfigFactory(school=school)
        response = admin_auth.patch(
            f"/api/v1/academics/workload-config/{config.id}/",
            {"max_periods_per_week": 35},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["max_periods_per_week"] == 35

    def test_student_cannot_manage_config(self, api_client, student_user):
        api_client.force_authenticate(user=student_user)
        response = api_client.get("/api/v1/academics/workload-config/")
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestTeacherWorkload:

    def test_workload_summary_requires_academic_year(self, admin_auth):
        response = admin_auth.get("/api/v1/academics/workload/summary/")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_workload_summary_empty(self, admin_auth, academic_year):
        response = admin_auth.get(f"/api/v1/academics/workload/summary/?academic_year={academic_year.id}")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

    def test_workload_summary_with_teacher(self, admin_auth, teacher_user, academic_year):
        response = admin_auth.get(
            f"/api/v1/academics/workload/summary/?academic_year={academic_year.id}&teacher_id={teacher_user.id}"
        )
        assert response.status_code == status.HTTP_200_OK

    def test_my_workload_endpoint(self, teacher_auth, academic_year, teacher_user):
        response = teacher_auth.get(f"/api/v1/academics/workload/my-workload/?academic_year={academic_year.id}")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["teacher_id"] == str(teacher_user.id)

    def test_student_cannot_access_my_workload(self, api_client, student_user, academic_year):
        api_client.force_authenticate(user=student_user)
        response = api_client.get(f"/api/v1/academics/workload/my-workload/?academic_year={academic_year.id}")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_overloaded_endpoint(self, admin_auth, academic_year):
        response = admin_auth.get(f"/api/v1/academics/workload/overloaded/?academic_year={academic_year.id}")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

    def test_create_snapshot(self, admin_auth, academic_year):
        response = admin_auth.post(
            "/api/v1/academics/workload/snapshot/",
            {
                "academic_year": academic_year.id,
                "week_start_date": "2026-09-01",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["snapshots_created"] == 0


# ─── Evaluation Criteria Tests ──────────────────────────────────────────────


@pytest.mark.django_db
class TestEvaluationCriteria:

    def test_list_criteria(self, admin_auth):
        response = admin_auth.get("/api/v1/academics/evaluation-criteria/")
        assert response.status_code == status.HTTP_200_OK

    def test_create_criteria(self, admin_auth):
        response = admin_auth.post(
            "/api/v1/academics/evaluation-criteria/",
            {
                "name": "Lesson Planning",
                "description": "Ability to plan effective lessons",
                "category": "planning",
                "max_score": 5,
                "weight": "1.5",
                "order": 1,
            },
            format="json",
        )
        assert response.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK)


# ─── Evaluation Template Tests ─────────────────────────────────────────────


@pytest.mark.django_db
class TestEvaluationTemplate:

    def test_list_templates(self, admin_auth):
        response = admin_auth.get("/api/v1/academics/evaluation-templates/")
        assert response.status_code == status.HTTP_200_OK

    def test_create_template(self, admin_auth, school):
        from tests.factories import EvaluationCriteriaFactory

        criteria = EvaluationCriteriaFactory(school=school)
        response = admin_auth.post(
            "/api/v1/academics/evaluation-templates/",
            {
                "name": "Classroom Observation",
                "description": "Standard classroom observation form",
                "eval_type": "observation",
                "criteria_ids": [criteria.id],
            },
            format="json",
        )
        assert response.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK)


# ─── Teacher Evaluation Tests ──────────────────────────────────────────────


@pytest.mark.django_db
class TestTeacherEvaluation:

    def test_list_evaluations(self, admin_auth):
        response = admin_auth.get("/api/v1/academics/evaluations/")
        assert response.status_code == status.HTTP_200_OK

    def test_create_evaluation(self, admin_auth, teacher_user, academic_year, school):
        from tests.factories import EvaluationTemplateFactory

        template = EvaluationTemplateFactory(school=school)
        response = admin_auth.post(
            "/api/v1/academics/evaluations/",
            {
                "teacher": str(teacher_user.id),
                "template": template.id,
                "academic_year": academic_year.id,
                "title": "Fall 2026 Evaluation",
                "evaluation_period": "Fall 2026",
            },
            format="json",
        )
        assert response.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK)
        assert response.data["status"] == "draft"

    def test_advance_status(self, admin_auth, teacher_user, academic_year, school):
        from services.academics.models import TeacherEvaluation
        from tests.factories import EvaluationTemplateFactory

        template = EvaluationTemplateFactory(school=school)
        evaluation = TeacherEvaluation.objects.create(
            teacher=teacher_user,
            template=template,
            academic_year=academic_year,
            title="Test Evaluation",
            status="draft",
            created_by=admin_auth.handler._view.request.user,
        )
        response = admin_auth.post(f"/api/v1/academics/evaluations/{evaluation.id}/advance-status/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "self_review"

    def test_submit_scores(self, admin_auth, teacher_user, academic_year, school):
        from services.academics.models import TeacherEvaluation
        from tests.factories import EvaluationCriteriaFactory, EvaluationTemplateFactory

        criteria = EvaluationCriteriaFactory(school=school)
        template = EvaluationTemplateFactory(school=school)
        evaluation = TeacherEvaluation.objects.create(
            teacher=teacher_user,
            template=template,
            academic_year=academic_year,
            title="Test Evaluation",
            status="draft",
            created_by=admin_auth.handler._view.request.user,
        )
        response = admin_auth.post(
            f"/api/v1/academics/evaluations/{evaluation.id}/submit-scores/",
            {
                "scores": [
                    {
                        "criterion_id": str(criteria.id),
                        "score": 4.5,
                        "evidence": "Great teaching",
                        "comments": "Excellent",
                    }
                ]
            },
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["overall_score"] is not None

    def test_add_comment(self, admin_auth, teacher_user, academic_year, school):
        from services.academics.models import TeacherEvaluation
        from tests.factories import EvaluationTemplateFactory

        template = EvaluationTemplateFactory(school=school)
        evaluation = TeacherEvaluation.objects.create(
            teacher=teacher_user,
            template=template,
            academic_year=academic_year,
            title="Test Evaluation",
            status="draft",
            created_by=admin_auth.handler._view.request.user,
        )
        response = admin_auth.post(
            f"/api/v1/academics/evaluations/{evaluation.id}/comments/",
            {
                "comment_type": "general",
                "content": "Keep up the good work!",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["content"] == "Keep up the good work!"

    def test_my_evaluations_endpoint(self, teacher_auth, teacher_user, academic_year, school):
        from services.academics.models import TeacherEvaluation
        from tests.factories import EvaluationTemplateFactory

        template = EvaluationTemplateFactory(school=school)
        TeacherEvaluation.objects.create(
            teacher=teacher_user,
            template=template,
            academic_year=academic_year,
            title="My Evaluation",
            status="draft",
            created_by=teacher_user,
        )
        response = teacher_auth.get("/api/v1/academics/evaluations/my-evaluations/")
        assert response.status_code == status.HTTP_200_OK

    def test_complete_evaluation(self, admin_auth, teacher_user, academic_year, school):
        from services.academics.models import TeacherEvaluation
        from tests.factories import EvaluationTemplateFactory

        template = EvaluationTemplateFactory(school=school)
        evaluation = TeacherEvaluation.objects.create(
            teacher=teacher_user,
            template=template,
            academic_year=academic_year,
            title="Test Evaluation",
            status="admin_review",
            created_by=admin_auth.handler._view.request.user,
        )
        response = admin_auth.post(
            f"/api/v1/academics/evaluations/{evaluation.id}/complete/",
            {
                "strength": "Excellent classroom management",
                "areas_for_growth": "Technology integration",
                "action_plan": "Attend PD workshop",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "completed"
        assert response.data["review_date"] is not None


# ---------------------------------------------------------------------------
# Academic Transcript Tests
# ---------------------------------------------------------------------------


class TestAcademicTranscript:
    """Tests for the AcademicTranscript model and API endpoints."""

    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.school = SchoolFactory()
        self.admin = AdminUserFactory(school=self.school)
        self.teacher = TeacherUserFactory(school=self.school)
        self.grade = GradeFactory(school=self.school)
        self.classroom = ClassroomFactory(school=self.school, grade=self.grade)
        self.academic_year = AcademicYearFactory(school=self.school)
        self.subject = SubjectFactory(school=self.school, grade=self.grade)
        self.student_user = StudentUserFactory(school=self.school)
        self.student = StudentFactory(user=self.student_user, school=self.school)
        self.client = APIClient()

    def test_create_transcript(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post(
            "/api/v1/academics/transcripts/",
            {
                "student": str(self.student.id),
                "academic_year": str(self.academic_year.id),
                "status": "draft",
                "total_marks": "800.00",
                "obtained_marks": "640.00",
                "percentage": "80.00",
                "gpa": "3.20",
                "grade_letter": "A",
                "attendance_days": 180,
                "total_school_days": 200,
                "attendance_percentage": "90.00",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["student"] == str(self.student.id)
        assert response.data["grade_letter"] == "A"
        assert float(response.data["percentage"]) == 80.0

    def test_list_transcripts(self):
        self.client.force_authenticate(self.admin)
        AcademicTranscriptFactory(
            student=self.student,
            academic_year=self.academic_year,
            generated_by=self.admin,
        )
        response = self.client.get("/api/v1/academics/transcripts/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_student_sees_own_transcript(self):
        AcademicTranscriptFactory(
            student=self.student,
            academic_year=self.academic_year,
            generated_by=self.admin,
        )  # noqa: E501
        self.client.force_authenticate(self.student_user)
        response = self.client.get("/api/v1/academics/transcripts/my-transcript/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_student_cannot_see_other_students_transcripts(self):
        other_user = StudentUserFactory(school=self.school)
        AcademicTranscriptFactory(  # noqa: F841
            student=self.student,
            academic_year=self.academic_year,
            generated_by=self.admin,
        )
        self.client.force_authenticate(other_user)
        response = self.client.get("/api/v1/academics/transcripts/my-transcript/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 0

    def test_verify_transcript(self):
        self.client.force_authenticate(self.admin)
        transcript = AcademicTranscriptFactory(
            student=self.student,
            academic_year=self.academic_year,
            generated_by=self.admin,
            status="draft",
        )
        response = self.client.post(
            f"/api/v1/academics/transcripts/{transcript.id}/verify/",
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "verified"
        assert response.data["verified_by"] == str(self.admin.id)

    def test_bulk_generate_transcripts(self):
        from services.students.models import Enrollment

        Enrollment.objects.create(
            student=self.student,
            classroom=self.classroom,
            academic_year=self.academic_year,
            status="active",
            is_active=True,
        )
        self.client.force_authenticate(self.admin)
        response = self.client.post(
            "/api/v1/academics/transcripts/bulk-generate/",
            {
                "classroom": str(self.classroom.id),
                "academic_year": str(self.academic_year.id),
            },
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["generated"] == 1

    def test_class_rankings(self):
        self.client.force_authenticate(self.admin)
        AcademicTranscriptFactory(
            student=self.student,
            academic_year=self.academic_year,
            percentage=Decimal("85.00"),
            generated_by=self.admin,
            status="generated",
        )
        other_user2 = StudentUserFactory(school=self.school)
        student2 = StudentFactory(user=other_user2, school=self.school)
        AcademicTranscriptFactory(
            student=student2,
            academic_year=self.academic_year,
            percentage=Decimal("90.00"),
            generated_by=self.admin,
            status="generated",
        )
        response = self.client.get(
            f"/api/v1/academics/transcripts/class-rankings/{self.academic_year.id}/",
        )
        assert response.status_code == status.HTTP_200_OK

    def test_duplicate_transcript_rejected(self):
        self.client.force_authenticate(self.admin)
        AcademicTranscriptFactory(
            student=self.student,
            academic_year=self.academic_year,
            generated_by=self.admin,
        )  # noqa: F841
        response = self.client.post(
            "/api/v1/academics/transcripts/generate/",
            {
                "student": str(self.student.id),
                "academic_year": str(self.academic_year.id),
            },
            format="json",
        )
        assert response.status_code == status.HTTP_409_CONFLICT

    def test_generate_transcript_missing_params(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post(
            "/api/v1/academics/transcripts/generate/",
            {},
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_verify_already_verified(self):
        self.client.force_authenticate(self.admin)
        transcript = AcademicTranscriptFactory(
            student=self.student,
            academic_year=self.academic_year,
            generated_by=self.admin,
            status="verified",
            verified_by=self.admin,
        )  # noqa: F841
        response = self.client.post(
            f"/api/v1/academics/transcripts/{transcript.id}/verify/",
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_non_admin_cannot_verify(self):
        self.client.force_authenticate(self.teacher)
        transcript = AcademicTranscriptFactory(
            student=self.student,
            academic_year=self.academic_year,
            generated_by=self.admin,
        )  # noqa: F841
        response = self.client.post(
            f"/api/v1/academics/transcripts/{transcript.id}/verify/",
            format="json",
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_transcript_number_auto_generated(self):
        transcript = AcademicTranscriptFactory(
            student=self.student,
            academic_year=self.academic_year,
            generated_by=self.admin,
        )
        assert transcript.transcript_number.startswith("TR-")
        assert len(transcript.transcript_number) > 10
