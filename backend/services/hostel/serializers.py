"""Hostel / Accommodation Management serializers."""

from rest_framework import serializers

from .models import (
    CheckoutProcess,
    ComplaintManagement,
    EmergencyContact,
    Hostel,
    HostelAllocation,
    HostelAttendance,
    HostelFee,
    HostelFeedback,
    HostelNotification,
    HostelReport,
    HostelRoom,
    HostelVisitor,
    InventoryManagement,
    LeaveManagement,
    MessAttendance,
    MessManagement,
    RoomInspection,
    RoomMaintenance,
    RoomTransfer,
)


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
            "id",
            "name",
            "code",
            "gender",
            "gender_display",
            "status",
            "status_display",
            "warden",
            "warden_name",
            "assistant_warden",
            "assistant_warden_name",
            "address",
            "phone",
            "total_floors",
            "rules",
            "amenities",
            "notes",
            "total_rooms",
            "total_beds",
            "occupied_beds",
            "available_beds",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_warden(self, value):
        # Hostels must stay within the tenant — the warden has to be a staff
        # member of the same school.
        user = self.context["request"].user
        if value.school_id != user.school_id:
            raise serializers.ValidationError("Warden must be in your school.")
        return value

    def validate_assistant_warden(self, value):
        # Hostels must stay within the tenant — the assistant warden has to be
        # a staff member of the same school.
        user = self.context["request"].user
        if value.school_id != user.school_id:
            raise serializers.ValidationError("Assistant warden must be in your school.")
        return value


class HostelRoomSerializer(serializers.ModelSerializer):
    room_type_display = serializers.CharField(source="get_room_type_display", read_only=True)
    hostel_name = serializers.CharField(source="hostel.name", read_only=True)
    occupied_beds = serializers.IntegerField(read_only=True)
    available_beds = serializers.IntegerField(read_only=True)

    class Meta:
        model = HostelRoom
        fields = [
            "id",
            "hostel",
            "hostel_name",
            "room_number",
            "floor",
            "room_type",
            "room_type_display",
            "capacity",
            "is_furnished",
            "has_ac",
            "has_attached_bathroom",
            "monthly_fee",
            "occupied_beds",
            "available_beds",
            "is_active",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate_hostel(self, value):
        # Rooms inherit tenant scope from their hostel — reject hostels from
        # another school.
        user = self.context["request"].user
        if value.school_id != user.school_id:
            raise serializers.ValidationError("Hostel not found in your school.")
        return value


class HostelAllocationSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    room_display = serializers.CharField(source="room.__str__", read_only=True)
    hostel_name = serializers.CharField(source="room.hostel.name", read_only=True)
    room_number = serializers.CharField(source="room.room_number", read_only=True)
    allocated_by_name = serializers.CharField(source="allocated_by.full_name", read_only=True, default=None)

    class Meta:
        model = HostelAllocation
        fields = [
            "id",
            "student",
            "student_name",
            "room",
            "room_display",
            "hostel_name",
            "room_number",
            "status",
            "check_in_date",
            "check_out_date",
            "fee_amount",
            "is_paid",
            "notes",
            "allocated_by",
            "allocated_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "allocated_by", "created_at", "updated_at"]

    def validate_student(self, value):
        # Allocations must stay within the tenant — the student has to belong
        # to the same school as the caller.
        user = self.context["request"].user
        if value.school_id != user.school_id:
            raise serializers.ValidationError("Student not found in your school.")
        return value

    def validate_room(self, value):
        # Allocations inherit tenant scope from the room (which belongs to a
        # hostel) — reject rooms from another school.
        user = self.context["request"].user
        if value.hostel.school_id != user.school_id:
            raise serializers.ValidationError("Room not found in your school.")
        return value


class HostelFeeSerializer(serializers.ModelSerializer):
    billing_cycle_display = serializers.CharField(source="get_billing_cycle_display", read_only=True)
    hostel_name = serializers.CharField(source="hostel.name", read_only=True)

    class Meta:
        model = HostelFee
        fields = [
            "id",
            "name",
            "hostel",
            "hostel_name",
            "room_type",
            "amount",
            "billing_cycle",
            "billing_cycle_display",
            "includes_meals",
            "includes_laundry",
            "includes_wifi",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate_hostel(self, value):
        # Fee structures must stay within the tenant — the hostel has to
        # belong to the same school as the caller.
        user = self.context["request"].user
        if value.school_id != user.school_id:
            raise serializers.ValidationError("Hostel not found in your school.")
        return value


class HostelVisitorSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student_visited.user.full_name", read_only=True)
    hostel_name = serializers.CharField(source="hostel.name", read_only=True)
    checked_in_by_name = serializers.CharField(source="checked_in_by.full_name", read_only=True, default=None)

    class Meta:
        model = HostelVisitor
        fields = [
            "id",
            "hostel",
            "hostel_name",
            "visitor_name",
            "phone",
            "id_proof",
            "student_visited",
            "student_name",
            "purpose",
            "in_time",
            "out_time",
            "relationship",
            "checked_in_by",
            "checked_in_by_name",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "checked_in_by", "created_at"]

    def validate_hostel(self, value):
        # Visitor logs must stay within the tenant — the hostel has to belong
        # to the same school as the caller.
        user = self.context["request"].user
        if value.school_id != user.school_id:
            raise serializers.ValidationError("Hostel not found in your school.")
        return value

    def validate_student_visited(self, value):
        # Visitor logs must stay within the tenant — the student visited has
        # to belong to the same school as the caller.
        user = self.context["request"].user
        if value.school_id != user.school_id:
            raise serializers.ValidationError("Student not found in your school.")
        return value


# =============================================================================
# Room Maintenance Serializers
# =============================================================================


class RoomMaintenanceSerializer(serializers.ModelSerializer):
    room_number = serializers.CharField(source="room.room_number", read_only=True)
    reported_by_name = serializers.CharField(source="reported_by.user.full_name", read_only=True, default=None)
    assigned_to_name = serializers.CharField(source="assigned_to.full_name", read_only=True, default=None)

    class Meta:
        model = RoomMaintenance
        fields = [
            "id",
            "room",
            "room_number",
            "maintenance_type",
            "description",
            "status",
            "priority",
            "reported_by",
            "reported_by_name",
            "assigned_to",
            "assigned_to_name",
            "reported_date",
            "scheduled_date",
            "completed_date",
            "estimated_cost",
            "actual_cost",
            "notes",
            "resolution_notes",
            "created_at",
        ]
        read_only_fields = ["id", "reported_date", "created_at"]


# =============================================================================
# Hostel Attendance Serializers
# =============================================================================


class HostelAttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="allocation.student.user.full_name", read_only=True)
    room_number = serializers.CharField(source="allocation.room.room_number", read_only=True)

    class Meta:
        model = HostelAttendance
        fields = [
            "id",
            "allocation",
            "student_name",
            "room_number",
            "date",
            "status",
            "check_in_time",
            "check_out_time",
            "is_in_campus",
            "recorded_by",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


# =============================================================================
# Leave Management Serializers
# =============================================================================


class LeaveManagementSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="allocation.student.user.full_name", read_only=True)
    approved_by_name = serializers.CharField(source="approved_by.full_name", read_only=True, default=None)

    class Meta:
        model = LeaveManagement
        fields = [
            "id",
            "allocation",
            "student_name",
            "leave_type",
            "reason",
            "status",
            "from_date",
            "to_date",
            "total_days",
            "approved_by",
            "approved_by_name",
            "approved_at",
            "rejection_reason",
            "parent_notified",
            "parent_consent",
            "emergency_contact",
            "emergency_phone",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "approved_at", "created_at"]


# =============================================================================
# Mess Management Serializers
# =============================================================================


class MessAttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="allocation.student.user.full_name", read_only=True)

    class Meta:
        model = MessAttendance
        fields = ["id", "mess_menu", "allocation", "student_name", "status", "recorded_at"]
        read_only_fields = ["id", "recorded_at"]


class MessManagementSerializer(serializers.ModelSerializer):
    hostel_name = serializers.CharField(source="hostel.name", read_only=True)
    attendance = MessAttendanceSerializer(many=True, read_only=True)

    class Meta:
        model = MessManagement
        fields = [
            "id",
            "hostel",
            "hostel_name",
            "date",
            "meal_type",
            "menu_items",
            "description",
            "is_vegetarian",
            "is_vegan",
            "is_halal",
            "is_gluten_free",
            "rating",
            "cost_per_meal",
            "is_active",
            "created_by",
            "attendance",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


# =============================================================================
# Complaint Management Serializers
# =============================================================================


class ComplaintManagementSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="allocation.student.user.full_name", read_only=True)
    assigned_to_name = serializers.CharField(source="assigned_to.full_name", read_only=True, default=None)
    resolved_by_name = serializers.CharField(source="resolved_by.full_name", read_only=True, default=None)

    class Meta:
        model = ComplaintManagement
        fields = [
            "id",
            "hostel",
            "allocation",
            "student_name",
            "complaint_type",
            "title",
            "description",
            "status",
            "priority",
            "assigned_to",
            "assigned_to_name",
            "resolution_notes",
            "resolved_at",
            "resolved_by",
            "resolved_by_name",
            "satisfaction_rating",
            "feedback",
            "is_anonymous",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "resolved_at", "created_at"]


# =============================================================================
# Room Inspection Serializers
# =============================================================================


class RoomInspectionSerializer(serializers.ModelSerializer):
    room_number = serializers.CharField(source="room.room_number", read_only=True)
    inspected_by_name = serializers.CharField(source="inspected_by.full_name", read_only=True, default=None)

    class Meta:
        model = RoomInspection
        fields = [
            "id",
            "room",
            "room_number",
            "inspection_type",
            "status",
            "scheduled_date",
            "completed_date",
            "cleanliness_rating",
            "orderliness_rating",
            "condition_rating",
            "inspected_by",
            "inspected_by_name",
            "issues_found",
            "has_issues",
            "notes",
            "action_required",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


# =============================================================================
# Inventory Management Serializers
# =============================================================================


class InventoryManagementSerializer(serializers.ModelSerializer):
    hostel_name = serializers.CharField(source="hostel.name", read_only=True)
    room_number = serializers.CharField(source="room.room_number", read_only=True, default=None)

    class Meta:
        model = InventoryManagement
        fields = [
            "id",
            "hostel",
            "hostel_name",
            "room",
            "room_number",
            "item_name",
            "item_category",
            "description",
            "quantity",
            "unit_price",
            "total_value",
            "status",
            "purchase_date",
            "warranty_expiry",
            "supplier",
            "last_inspected_date",
            "condition_notes",
            "asset_tag",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


# =============================================================================
# Hostel Reports Serializers
# =============================================================================


class HostelReportSerializer(serializers.ModelSerializer):
    generated_by_name = serializers.CharField(source="generated_by.full_name", read_only=True, default=None)

    class Meta:
        model = HostelReport
        fields = [
            "id",
            "hostel",
            "title",
            "report_type",
            "status",
            "period_start",
            "period_end",
            "summary",
            "findings",
            "recommendations",
            "total_rooms",
            "occupied_rooms",
            "occupancy_rate",
            "total_complaints",
            "resolved_complaints",
            "total_maintenance",
            "completed_maintenance",
            "generated_by",
            "generated_by_name",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


# =============================================================================
# Emergency Contacts Serializers
# =============================================================================


class EmergencyContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyContact
        fields = [
            "id",
            "hostel",
            "contact_type",
            "name",
            "phone_primary",
            "phone_secondary",
            "email",
            "is_available_24x7",
            "available_hours",
            "location",
            "is_active",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


# =============================================================================
# Room Transfer Serializers
# =============================================================================


class RoomTransferSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="allocation.student.user.full_name", read_only=True)
    from_room_number = serializers.CharField(source="from_room.room_number", read_only=True)
    to_room_number = serializers.CharField(source="to_room.room_number", read_only=True)
    approved_by_name = serializers.CharField(source="approved_by.full_name", read_only=True, default=None)

    class Meta:
        model = RoomTransfer
        fields = [
            "id",
            "allocation",
            "student_name",
            "from_room",
            "from_room_number",
            "to_room",
            "to_room_number",
            "reason",
            "status",
            "approved_by",
            "approved_by_name",
            "approved_at",
            "rejection_reason",
            "requested_date",
            "transfer_date",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "approved_at", "requested_date", "created_at"]


# =============================================================================
# Checkout Process Serializers
# =============================================================================


class CheckoutProcessSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="allocation.student.user.full_name", read_only=True)
    approved_by_name = serializers.CharField(source="approved_by.full_name", read_only=True, default=None)

    class Meta:
        model = CheckoutProcess
        fields = [
            "id",
            "allocation",
            "student_name",
            "status",
            "checkout_date",
            "room_inspected",
            "inspection_notes",
            "damage_detected",
            "damage_description",
            "damage_charge",
            "items_returned",
            "missing_items",
            "pending_dues",
            "security_deposit_refund",
            "final_amount",
            "keys_returned",
            "approved_by",
            "approved_by_name",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


# =============================================================================
# Hostel Notifications Serializers
# =============================================================================


class HostelNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = HostelNotification
        fields = [
            "id",
            "hostel",
            "notification_type",
            "status",
            "title",
            "message",
            "recipient_type",
            "recipients",
            "sent_at",
            "read_count",
            "is_priority",
            "created_by",
            "created_at",
        ]
        read_only_fields = ["id", "sent_at", "created_at"]


# =============================================================================
# Hostel Feedback Serializers
# =============================================================================


class HostelFeedbackSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="allocation.student.user.full_name", read_only=True)
    responded_by_name = serializers.CharField(source="responded_by.full_name", read_only=True, default=None)

    class Meta:
        model = HostelFeedback
        fields = [
            "id",
            "hostel",
            "allocation",
            "student_name",
            "feedback_type",
            "rating",
            "title",
            "comment",
            "suggestion",
            "is_anonymous",
            "response",
            "responded_by",
            "responded_by_name",
            "responded_at",
            "created_at",
        ]
        read_only_fields = ["id", "responded_at", "created_at"]
