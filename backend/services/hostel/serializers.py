"""Hostel / Accommodation Management serializers."""

from rest_framework import serializers
from .models import Hostel, HostelRoom, HostelAllocation, HostelFee, HostelVisitor


class HostelSerializer(serializers.ModelSerializer):
    gender_display = serializers.CharField(source="get_gender_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    warden_name = serializers.CharField(source="warden.full_name", read_only=True, default=None)
    assistant_warden_name = serializers.CharField(source="assistant_warden.full_name", read_only=True, default=None)
    total_rooms = serializers.IntegerField(read_only=True)
    total_beds = serializers.IntegerField(read_only=True)
    occupied_beds = serializers.IntegerField(read_only=True)
    available_beds = serializers.IntegerField(read_only=True)

    class Meta:
        model = Hostel
        fields = [
            "id", "name", "code", "gender", "gender_display", "status", "status_display",
            "warden", "warden_name", "assistant_warden", "assistant_warden_name",
            "address", "phone", "total_floors", "rules", "amenities", "notes",
            "total_rooms", "total_beds", "occupied_beds", "available_beds",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class HostelRoomSerializer(serializers.ModelSerializer):
    room_type_display = serializers.CharField(source="get_room_type_display", read_only=True)
    hostel_name = serializers.CharField(source="hostel.name", read_only=True)
    occupied_beds = serializers.IntegerField(read_only=True)
    available_beds = serializers.IntegerField(read_only=True)

    class Meta:
        model = HostelRoom
        fields = [
            "id", "hostel", "hostel_name", "room_number", "floor", "room_type",
            "room_type_display", "capacity", "is_furnished", "has_ac",
            "has_attached_bathroom", "monthly_fee",
            "occupied_beds", "available_beds",
            "is_active", "notes", "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class HostelAllocationSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    room_display = serializers.CharField(source="room.__str__", read_only=True)
    hostel_name = serializers.CharField(source="room.hostel.name", read_only=True)
    room_number = serializers.CharField(source="room.room_number", read_only=True)
    allocated_by_name = serializers.CharField(source="allocated_by.full_name", read_only=True, default=None)

    class Meta:
        model = HostelAllocation
        fields = [
            "id", "student", "student_name", "room", "room_display",
            "hostel_name", "room_number",
            "status", "check_in_date", "check_out_date",
            "fee_amount", "is_paid", "notes",
            "allocated_by", "allocated_by_name",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class HostelFeeSerializer(serializers.ModelSerializer):
    billing_cycle_display = serializers.CharField(source="get_billing_cycle_display", read_only=True)
    hostel_name = serializers.CharField(source="hostel.name", read_only=True)

    class Meta:
        model = HostelFee
        fields = [
            "id", "name", "hostel", "hostel_name", "room_type",
            "amount", "billing_cycle", "billing_cycle_display",
            "includes_meals", "includes_laundry", "includes_wifi",
            "is_active", "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class HostelVisitorSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student_visited.user.full_name", read_only=True)
    hostel_name = serializers.CharField(source="hostel.name", read_only=True)
    checked_in_by_name = serializers.CharField(source="checked_in_by.full_name", read_only=True, default=None)

    class Meta:
        model = HostelVisitor
        fields = [
            "id", "hostel", "hostel_name", "visitor_name", "phone",
            "id_proof", "student_visited", "student_name",
            "purpose", "in_time", "out_time", "relationship",
            "checked_in_by", "checked_in_by_name", "notes", "created_at",
        ]
        read_only_fields = ["id", "created_at"]
