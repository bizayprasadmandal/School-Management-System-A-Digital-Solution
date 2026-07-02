"""Reporting serializers — lightweight response shapes for analytics endpoints."""
from rest_framework import serializers


class DashboardStatsSerializer(serializers.Serializer):
    total_students = serializers.IntegerField()
    total_teachers = serializers.IntegerField()
    total_classrooms = serializers.IntegerField()
    attendance_today_pct = serializers.FloatField()
    fees_collected_month = serializers.FloatField()
    fees_outstanding = serializers.FloatField()
    student_delta_pct = serializers.FloatField()
    attendance_delta_pct = serializers.FloatField()


class AttendanceDailySerializer(serializers.Serializer):
    date = serializers.DateField()
    total = serializers.IntegerField()
    present = serializers.IntegerField()
    absent = serializers.IntegerField()
    late = serializers.IntegerField()
    excused = serializers.IntegerField()


class FeeStatusSerializer(serializers.Serializer):
    status = serializers.CharField()
    count = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=14, decimal_places=2)
