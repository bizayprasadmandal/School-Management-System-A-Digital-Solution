import django_filters
from .models import Student


class StudentFilter(django_filters.FilterSet):
    gender = django_filters.ChoiceFilter(choices=Student.Gender.choices)
    is_active = django_filters.BooleanFilter()
    admission_date_after = django_filters.DateFilter(field_name="admission_date", lookup_expr="gte")
    admission_date_before = django_filters.DateFilter(field_name="admission_date", lookup_expr="lte")
    grade = django_filters.NumberFilter(field_name="enrollments__classroom__grade")
    classroom = django_filters.NumberFilter(field_name="enrollments__classroom")

    class Meta:
        model = Student
        fields = ["gender", "is_active", "grade", "classroom"]
