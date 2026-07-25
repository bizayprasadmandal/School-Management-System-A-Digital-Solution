"""
Test Factories — factory_boy definitions for all SMS models.
Use these in tests to create realistic fixture data with one line.
"""

import factory
import factory.django
from factory import LazyAttribute, SubFactory, Sequence, fuzzy
from datetime import date, timedelta
from decimal import Decimal
import random


class SchoolFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "auth_service.School"
        django_get_or_create = ["code"]

    name = factory.Sequence(lambda n: f"Test School {n}")
    code = factory.Sequence(lambda n: f"SCH{n:03d}")
    subdomain = factory.Sequence(lambda n: f"school{n}")
    address = factory.Faker("street_address")
    phone = factory.Sequence(lambda n: f"+1-555-{n:04d}")
    email = factory.LazyAttribute(lambda o: f"admin@{o.subdomain}.edu")
    timezone = "UTC"
    is_active = True
    subscription_tier = "standard"


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "auth_service.User"
        django_get_or_create = ["email"]

    email = factory.Sequence(lambda n: f"user{n}@school.edu")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    password = factory.PostGenerationMethodCall("set_password", "TestPass@1234")
    role = "student"
    school = SubFactory(SchoolFactory)
    is_active = True


class AdminUserFactory(UserFactory):
    role = "school_admin"
    is_staff = True


class TeacherUserFactory(UserFactory):
    role = "teacher"


class StudentUserFactory(UserFactory):
    role = "student"


class ParentUserFactory(UserFactory):
    role = "parent"


class AcademicYearFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "students.AcademicYear"

    school = SubFactory(SchoolFactory)
    name = factory.Sequence(lambda n: f"202{n}-202{n+1}")
    start_date = factory.LazyFunction(lambda: date.today().replace(month=9, day=1))
    end_date = factory.LazyFunction(lambda: (date.today() + timedelta(days=365)).replace(month=6, day=30))
    is_current = True


class GradeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "students.Grade"

    school = SubFactory(SchoolFactory)
    name = factory.Sequence(lambda n: f"Grade {n+1}")
    level = factory.Sequence(lambda n: n + 1)


class ClassroomFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "students.Classroom"

    school = SubFactory(SchoolFactory)
    grade = SubFactory(GradeFactory)
    name = factory.Sequence(lambda n: f"{n+1}A")
    capacity = 35
    academic_year = SubFactory(AcademicYearFactory)
    class_teacher = SubFactory(TeacherUserFactory)


class StudentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "students.Student"

    user = SubFactory(StudentUserFactory)
    school = factory.SelfAttribute("user.school")
    admission_number = factory.Sequence(lambda n: f"ADM-2024-{n:04d}")
    date_of_birth = factory.Faker("date_of_birth", minimum_age=5, maximum_age=18)
    gender = factory.fuzzy.FuzzyChoice(["M", "F"])
    address = factory.Faker("street_address")
    city = factory.Faker("city")
    state = factory.Faker("state")
    country = factory.Faker("country")
    admission_date = factory.LazyFunction(date.today)
    is_active = True


class GuardianFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "students.Guardian"

    user = SubFactory(ParentUserFactory)
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.Faker("email")
    phone = factory.Sequence(lambda n: f"+1-555-{n:04d}")


class EnrollmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "students.Enrollment"

    student = SubFactory(StudentFactory)
    classroom = SubFactory(ClassroomFactory)
    academic_year = SubFactory(AcademicYearFactory)
    status = "active"
    is_active = True


class SubjectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "academics.Subject"

    school = SubFactory(SchoolFactory)
    name = factory.Sequence(lambda n: f"Subject {n}")
    code = factory.Sequence(lambda n: f"SUB{n:03d}")
    grade = SubFactory(GradeFactory)
    max_marks = 100
    pass_marks = 40
    is_core = True
    is_active = True


class TeacherProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "academics.TeacherProfile"

    user = SubFactory(TeacherUserFactory)
    school = factory.SelfAttribute("user.school")
    employee_id = factory.Sequence(lambda n: f"EMP{n:04d}")
    gender = "M"
    qualification = "bachelor"
    joining_date = factory.LazyFunction(date.today)
    is_active = True


class TeacherAssignmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "academics.TeacherAssignment"

    teacher = SubFactory(TeacherUserFactory)
    subject = SubFactory(SubjectFactory)
    classroom = SubFactory(ClassroomFactory)
    academic_year = SubFactory(AcademicYearFactory)
    is_primary = True


class AttendanceRecordFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "attendance.AttendanceRecord"

    student = SubFactory(StudentFactory)
    classroom = SubFactory(ClassroomFactory)
    academic_year = SubFactory(AcademicYearFactory)
    date = factory.LazyFunction(date.today)
    status = "P"


class ExamTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "gradebook.ExamType"

    school = SubFactory(SchoolFactory)
    name = factory.Sequence(lambda n: f"Exam Type {n}")
    weightage = Decimal("50.00")
    is_terminal = False


class ExamFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "gradebook.Exam"

    school = SubFactory(SchoolFactory)
    academic_year = SubFactory(AcademicYearFactory)
    exam_type = SubFactory(ExamTypeFactory)
    name = factory.Sequence(lambda n: f"Midterm Exam {n}")
    start_date = factory.LazyFunction(date.today)
    end_date = factory.LazyFunction(lambda: date.today() + timedelta(days=7))
    status = "scheduled"


class ExamScheduleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "gradebook.ExamSchedule"

    exam = SubFactory(ExamFactory)
    subject = SubFactory(SubjectFactory)
    classroom = SubFactory(ClassroomFactory)
    date = factory.LazyFunction(date.today)
    start_time = "09:00"
    end_time = "11:00"
    max_marks = Decimal("100.00")
    passing_marks = Decimal("40.00")


class GradeRecordFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "gradebook.Grade"

    student = SubFactory(StudentFactory)
    exam_schedule = SubFactory(ExamScheduleFactory)
    marks_obtained = factory.LazyFunction(lambda: Decimal(str(random.randint(30, 100))))
    is_absent = False


class FeeCategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "fees.FeeCategory"

    school = SubFactory(SchoolFactory)
    name = factory.Sequence(lambda n: f"Fee Category {n}")
    recurrence = "monthly"
    is_mandatory = True


class FeeStructureFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "fees.FeeStructure"

    school = SubFactory(SchoolFactory)
    academic_year = SubFactory(AcademicYearFactory)
    grade = SubFactory(GradeFactory)
    fee_category = SubFactory(FeeCategoryFactory)
    amount = Decimal("500.00")
    due_day = 10
    is_active = True


class FeeInvoiceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "fees.FeeInvoice"

    invoice_number = factory.Sequence(lambda n: f"INV-{n:06d}")
    student = SubFactory(StudentFactory)
    academic_year = SubFactory(AcademicYearFactory)
    fee_structure = SubFactory(FeeStructureFactory)
    due_date = factory.LazyFunction(lambda: date.today() + timedelta(days=30))
    base_amount = Decimal("500.00")
    total_amount = Decimal("500.00")
    paid_amount = Decimal("0.00")
    status = "unpaid"


class AnnouncementFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "communication.Announcement"

    school = SubFactory(SchoolFactory)
    title = factory.Faker("sentence", nb_words=6)
    content = factory.Faker("paragraph")
    priority = "normal"
    audience = "all"
    is_draft = False
    created_by = SubFactory(AdminUserFactory)


class NotificationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "communication.Notification"

    user = SubFactory(UserFactory)
    title = factory.Faker("sentence", nb_words=5)
    body = factory.Faker("paragraph", nb_sentences=2)
    channel = "in_app"
    status = "sent"


class PeriodFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "timetable.Period"

    school = SubFactory(SchoolFactory)
    name = factory.Sequence(lambda n: f"Period {n+1}")
    period_number = factory.Sequence(lambda n: n + 1)
    start_time = factory.Sequence(lambda n: f"{8+n:02d}:00")
    end_time = factory.Sequence(lambda n: f"{8+n:02d}:45")
    is_break = False


class TimetableSlotFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "timetable.TimetableSlot"

    classroom = SubFactory(ClassroomFactory)
    assignment = SubFactory(TeacherAssignmentFactory)
    period = SubFactory(PeriodFactory)
    day_of_week = factory.fuzzy.FuzzyChoice(range(5))
    academic_year = SubFactory(AcademicYearFactory)


class LessonPlanFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "academics.LessonPlan"

    assignment = SubFactory(TeacherAssignmentFactory)
    title = factory.Sequence(lambda n: f"Lesson Plan {n}")
    topic = factory.Faker("word")
    objectives = factory.Faker("paragraph", nb_sentences=2)
    content = factory.Faker("paragraph", nb_sentences=3)
    date = factory.LazyFunction(date.today)
    duration_minutes = 45
    status = "draft"


class SchoolEventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "timetable.SchoolEvent"

    school = SubFactory(SchoolFactory)
    title = factory.Faker("sentence", nb_words=4)
    event_type = factory.fuzzy.FuzzyChoice(["holiday", "exam", "sports", "cultural", "ptm"])
    start_date = factory.LazyFunction(date.today)
    end_date = factory.LazyFunction(date.today)
    is_school_wide = True
    created_by = SubFactory(AdminUserFactory)
