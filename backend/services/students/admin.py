"""Django Admin registrations for students."""

from django.contrib import admin

from .models import (
    AcademicYear,
    Classroom,
    Document,
    Enrollment,
    Grade,
    Guardian,
    ParentProfile,
    SiblingTracking,
    Student,
    StudentAcademicAdvisor,
    StudentAchievement,
    StudentActivity,
    StudentArchive,
    StudentAward,
    StudentCareerGuidance,
    StudentCategory,
    StudentCategoryMembership,
    StudentClub,
    StudentContact,
    StudentCustomField,
    StudentCustomFieldValue,
    StudentDiscipline,
    StudentFeedback,
    StudentFinancialAid,
    StudentGraduation,
    StudentGuardian,
    StudentIDActivity,
    StudentIDCard,
    StudentInternship,
    StudentLearningStyle,
    StudentMealPlan,
    StudentMedicalRecord,
    StudentMentor,
    StudentNote,
    StudentParentCommunication,
    StudentParking,
    StudentPhoto,
    StudentPortfolio,
    StudentScholarship,
    StudentSocialMedia,
    StudentStatusHistory,
    StudentTag,
    StudentTagAssignment,
    StudentTransfer,
    StudentTransportAssignment,
    StudentTutoring,
    StudentVolunteer,
    StudentWellness,
)


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ["name", "school"]
    list_filter = ["school"]
    search_fields = ["name"]


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ["name", "school"]
    list_filter = ["school"]
    search_fields = ["name"]


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ["name", "school"]
    list_filter = ["school"]
    search_fields = ["name"]


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "is_active", "created_at"]
    list_filter = ["school", "is_active"]
    search_fields = ["id"]


@admin.register(Guardian)
class GuardianAdmin(admin.ModelAdmin):
    list_display = ["id"]
    list_filter = []
    search_fields = ["id"]


@admin.register(StudentGuardian)
class StudentGuardianAdmin(admin.ModelAdmin):
    list_display = ["id"]
    list_filter = []
    search_fields = ["id"]


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ["id", "status", "is_active"]
    list_filter = ["is_active", "status"]
    search_fields = ["id"]


@admin.register(ParentProfile)
class ParentProfileAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "created_at"]
    list_filter = ["school"]
    search_fields = ["id"]


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ["id"]
    list_filter = []
    search_fields = ["id"]


@admin.register(StudentContact)
class StudentContactAdmin(admin.ModelAdmin):
    list_display = ["id", "created_at"]
    list_filter = []
    search_fields = ["id"]


@admin.register(StudentMedicalRecord)
class StudentMedicalRecordAdmin(admin.ModelAdmin):
    list_display = ["id", "created_at"]
    list_filter = []
    search_fields = ["id"]


@admin.register(StudentCustomField)
class StudentCustomFieldAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "is_active", "created_at"]
    list_filter = ["school", "is_active"]
    search_fields = ["name"]


@admin.register(StudentCustomFieldValue)
class StudentCustomFieldValueAdmin(admin.ModelAdmin):
    list_display = ["id", "created_at"]
    list_filter = []
    search_fields = ["id"]


@admin.register(StudentPhoto)
class StudentPhotoAdmin(admin.ModelAdmin):
    list_display = ["id", "created_at"]
    list_filter = []
    search_fields = ["id"]


@admin.register(StudentIDCard)
class StudentIDCardAdmin(admin.ModelAdmin):
    list_display = ["id", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["id"]


@admin.register(StudentStatusHistory)
class StudentStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ["id", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["id"]


@admin.register(SiblingTracking)
class SiblingTrackingAdmin(admin.ModelAdmin):
    list_display = ["id", "created_at"]
    list_filter = []
    search_fields = ["id"]


@admin.register(StudentCategory)
class StudentCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "is_active", "created_at"]
    list_filter = ["school", "is_active"]
    search_fields = ["name"]


@admin.register(StudentCategoryMembership)
class StudentCategoryMembershipAdmin(admin.ModelAdmin):
    list_display = ["id", "is_active", "created_at"]
    list_filter = ["is_active"]
    search_fields = ["id"]


@admin.register(StudentTag)
class StudentTagAdmin(admin.ModelAdmin):
    list_display = ["name", "school", "is_active", "created_at"]
    list_filter = ["school", "is_active"]
    search_fields = ["name"]


@admin.register(StudentTagAssignment)
class StudentTagAssignmentAdmin(admin.ModelAdmin):
    list_display = ["id", "created_at"]
    list_filter = []
    search_fields = ["id"]


@admin.register(StudentNote)
class StudentNoteAdmin(admin.ModelAdmin):
    list_display = ["id", "created_at"]
    list_filter = []
    search_fields = ["id"]


@admin.register(StudentArchive)
class StudentArchiveAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(StudentSocialMedia)
class StudentSocialMediaAdmin(admin.ModelAdmin):
    list_display = ["id", "is_active", "created_at"]
    list_filter = ["is_active"]
    search_fields = ["id"]


@admin.register(StudentPortfolio)
class StudentPortfolioAdmin(admin.ModelAdmin):
    list_display = ["id", "created_at"]
    list_filter = []
    search_fields = ["id"]


@admin.register(StudentWellness)
class StudentWellnessAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(StudentLearningStyle)
class StudentLearningStyleAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "created_at"]
    list_filter = ["school"]
    search_fields = ["id"]


@admin.register(StudentAchievement)
class StudentAchievementAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "created_at"]
    list_filter = ["school"]
    search_fields = ["id"]


@admin.register(StudentClub)
class StudentClubAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "is_active", "created_at"]
    list_filter = ["school", "is_active"]
    search_fields = ["id"]


@admin.register(StudentActivity)
class StudentActivityAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "is_active", "created_at"]
    list_filter = ["school", "is_active"]
    search_fields = ["id"]


@admin.register(StudentAward)
class StudentAwardAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "created_at"]
    list_filter = ["school"]
    search_fields = ["id"]


@admin.register(StudentDiscipline)
class StudentDisciplineAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "created_at"]
    list_filter = ["school"]
    search_fields = ["id"]


@admin.register(StudentTutoring)
class StudentTutoringAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(StudentMentor)
class StudentMentorAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(StudentCareerGuidance)
class StudentCareerGuidanceAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "created_at"]
    list_filter = ["school"]
    search_fields = ["id"]


@admin.register(StudentParentCommunication)
class StudentParentCommunicationAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "created_at"]
    list_filter = ["school"]
    search_fields = ["id"]


@admin.register(StudentAcademicAdvisor)
class StudentAcademicAdvisorAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(StudentTransfer)
class StudentTransferAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(StudentGraduation)
class StudentGraduationAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(StudentVolunteer)
class StudentVolunteerAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "created_at"]
    list_filter = ["school"]
    search_fields = ["id"]


@admin.register(StudentInternship)
class StudentInternshipAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(StudentScholarship)
class StudentScholarshipAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(StudentFinancialAid)
class StudentFinancialAidAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(StudentTransportAssignment)
class StudentTransportAssignmentAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "is_active", "created_at"]
    list_filter = ["school", "is_active"]
    search_fields = ["id"]


@admin.register(StudentMealPlan)
class StudentMealPlanAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(StudentParking)
class StudentParkingAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "status", "created_at"]
    list_filter = ["school", "status"]
    search_fields = ["id"]


@admin.register(StudentIDActivity)
class StudentIDActivityAdmin(admin.ModelAdmin):
    list_display = ["id", "school"]
    list_filter = ["school"]
    search_fields = ["id"]


@admin.register(StudentFeedback)
class StudentFeedbackAdmin(admin.ModelAdmin):
    list_display = ["id", "school", "created_at"]
    list_filter = ["school"]
    search_fields = ["id"]
