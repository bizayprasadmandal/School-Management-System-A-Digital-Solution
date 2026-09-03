"""Serializers for hostel."""

from rest_framework import serializers

from .models import (
    CheckoutProcess,
    CommonAreaBooking,
    ComplaintManagement,
    EmergencyContact,
    Hostel,
    HostelAllocation,
    HostelAsset,
    HostelAssetTransfer,
    HostelAttendance,
    HostelAttendanceAlert,
    HostelEmergencyDrill,
    HostelEmergencyProtocol,
    HostelEvent,
    HostelEventParticipant,
    HostelFee,
    HostelFeedback,
    HostelFeePayment,
    HostelInspectionSchedule,
    HostelNotification,
    HostelReport,
    HostelRoom,
    HostelVisitor,
    InventoryManagement,
    LaundryService,
    LeaveManagement,
    MessAttendance,
    MessDietaryRequest,
    MessFeedback,
    MessManagement,
    MessMenuPlan,
    RoomInspection,
    RoomKey,
    RoomMaintenance,
    RoommateAssignment,
    RoommateMatchRequest,
    RoommatePreference,
    RoomTransfer,
    VisitorPass,
    WellnessCheck,
)


class HostelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hostel
        fields = [
            "id",
            "school",
            "id",
            "name",
            "code",
            "gender",
            "status",
            "warden",
            "assistant_warden",
            "address",
            "phone",
            "total_floors",
            "rules",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "school"]

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
    class Meta:
        model = HostelRoom
        fields = [
            "id",
            "hostel",
            "room_number",
            "floor",
            "room_type",
            "capacity",
            "is_furnished",
            "has_ac",
            "has_attached_bathroom",
            "monthly_fee",
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
    class Meta:
        model = HostelAllocation
        fields = [
            "id",
            "id",
            "student",
            "room",
            "status",
            "check_in_date",
            "check_out_date",
            "fee_amount",
            "is_paid",
            "notes",
            "allocated_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

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
    class Meta:
        model = HostelFee
        fields = [
            "id",
            "school",
            "id",
            "name",
            "hostel",
            "room_type",
            "amount",
            "billing_cycle",
            "includes_meals",
            "includes_laundry",
            "includes_wifi",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "school"]

    def validate_hostel(self, value):
        # Fee structures must stay within the tenant — the hostel has to
        # belong to the same school as the caller.
        user = self.context["request"].user
        if value.school_id != user.school_id:
            raise serializers.ValidationError("Hostel not found in your school.")
        return value


class HostelVisitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = HostelVisitor
        fields = [
            "id",
            "id",
            "hostel",
            "visitor_name",
            "phone",
            "id_proof",
            "student_visited",
            "purpose",
            "in_time",
            "out_time",
            "relationship",
            "checked_in_by",
            "notes",
        ]
        read_only_fields = ["id", "created_at"]

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


class RoomMaintenanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomMaintenance
        fields = [
            "id",
            "id",
            "room",
            "maintenance_type",
            "description",
            "status",
            "priority",
            "reported_by",
            "assigned_to",
            "reported_date",
            "scheduled_date",
            "completed_date",
            "estimated_cost",
        ]
        read_only_fields = ["id", "updated_at"]


class HostelAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = HostelAttendance
        fields = [
            "id",
            "id",
            "allocation",
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


class LeaveManagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveManagement
        fields = [
            "id",
            "id",
            "allocation",
            "leave_type",
            "reason",
            "status",
            "from_date",
            "to_date",
            "total_days",
            "approved_by",
            "approved_at",
            "rejection_reason",
            "parent_notified",
            "parent_consent",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class MessManagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessManagement
        fields = [
            "id",
            "id",
            "hostel",
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
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class MessAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessAttendance
        fields = ["id", "id", "mess_menu", "allocation", "status", "recorded_at"]
        read_only_fields = ["id"]


class ComplaintManagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplaintManagement
        fields = [
            "id",
            "id",
            "hostel",
            "allocation",
            "complaint_type",
            "title",
            "description",
            "status",
            "priority",
            "assigned_to",
            "resolution_notes",
            "resolved_at",
            "resolved_by",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class RoomInspectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomInspection
        fields = [
            "id",
            "id",
            "room",
            "inspection_type",
            "status",
            "scheduled_date",
            "completed_date",
            "cleanliness_rating",
            "orderliness_rating",
            "condition_rating",
            "inspected_by",
            "issues_found",
            "has_issues",
            "notes",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class InventoryManagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryManagement
        fields = [
            "id",
            "id",
            "hostel",
            "room",
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
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class HostelReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = HostelReport
        fields = [
            "id",
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
        ]
        read_only_fields = ["id", "created_at"]


class EmergencyContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyContact
        fields = [
            "id",
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
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class RoomTransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomTransfer
        fields = [
            "id",
            "id",
            "allocation",
            "from_room",
            "to_room",
            "reason",
            "status",
            "approved_by",
            "approved_at",
            "rejection_reason",
            "requested_date",
            "transfer_date",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class CheckoutProcessSerializer(serializers.ModelSerializer):
    class Meta:
        model = CheckoutProcess
        fields = [
            "id",
            "id",
            "allocation",
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
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class HostelNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = HostelNotification
        fields = [
            "id",
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
        read_only_fields = ["id", "created_at"]


class HostelFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = HostelFeedback
        fields = [
            "id",
            "id",
            "hostel",
            "allocation",
            "feedback_type",
            "rating",
            "title",
            "comment",
            "suggestion",
            "is_anonymous",
            "response",
            "responded_by",
            "responded_at",
        ]
        read_only_fields = ["id", "created_at"]


class RoommatePreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoommatePreference
        fields = [
            "id",
            "school",
            "id",
            "student",
            "sleep_time",
            "wake_time",
            "is_light_sleeper",
            "study_habits",
            "prefers_study_at",
            "visitor_frequency",
            "is_social",
            "smoking",
            "snoring",
            "neatness_level",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class RoommateAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoommateAssignment
        fields = ["id", "id", "room", "student", "allocation", "match_score", "assigned_date", "is_active", "notes"]
        read_only_fields = ["id"]


class RoomKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomKey
        fields = [
            "id",
            "id",
            "room",
            "key_number",
            "status",
            "allocated_to",
            "issued_date",
            "return_date",
            "replacement_cost",
            "reported_lost_date",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class LaundryServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LaundryService
        fields = [
            "id",
            "school",
            "id",
            "allocation",
            "status",
            "garment_type",
            "quantity",
            "description",
            "pickup_date",
            "pickup_time",
            "delivery_date",
            "delivery_time",
            "total_cost",
            "paid",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class CommonAreaBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommonAreaBooking
        fields = [
            "id",
            "id",
            "hostel",
            "student",
            "area_type",
            "area_name",
            "status",
            "booking_date",
            "start_time",
            "end_time",
            "group_size",
            "additional_members",
            "purpose",
            "rules_acknowledged",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class WellnessCheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = WellnessCheck
        fields = [
            "id",
            "school",
            "id",
            "student",
            "allocation",
            "checked_by",
            "check_type",
            "status",
            "check_date",
            "physical_wellbeing",
            "emotional_state",
            "room_condition",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class VisitorPassSerializer(serializers.ModelSerializer):
    class Meta:
        model = VisitorPass
        fields = [
            "id",
            "school",
            "id",
            "hostel",
            "resident",
            "visitor_name",
            "visitor_phone",
            "visitor_id_number",
            "relationship",
            "status",
            "visit_date",
            "expected_arrival",
            "expected_departure",
        ]
        read_only_fields = ["id", "created_at"]


class RoommateMatchRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoommateMatchRequest
        fields = [
            "id",
            "id",
            "requester",
            "requested",
            "status",
            "message",
            "response_message",
            "responded_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class MessMenuPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessMenuPlan
        fields = [
            "id",
            "id",
            "hostel",
            "meal_type",
            "day_of_week",
            "week_number",
            "main_course",
            "side_dish",
            "bread_rice",
            "dessert",
            "beverage",
            "is_vegetarian",
            "is_vegan",
            "is_gluten_free",
            "calories",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class MessDietaryRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessDietaryRequest
        fields = [
            "id",
            "school",
            "id",
            "student",
            "allocation",
            "diet_type",
            "status",
            "medical_reason",
            "doctor_note",
            "start_date",
            "end_date",
            "approved_by",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class HostelAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = HostelAsset
        fields = [
            "id",
            "id",
            "room",
            "hostel",
            "asset_name",
            "asset_tag",
            "description",
            "condition",
            "purchase_date",
            "purchase_cost",
            "warranty_expiry",
            "last_inspected",
            "is_active",
            "notes",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class HostelAssetTransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = HostelAssetTransfer
        fields = [
            "id",
            "id",
            "asset",
            "from_room",
            "to_room",
            "transferred_by",
            "transfer_date",
            "reason",
            "condition_at_transfer",
            "notes",
        ]
        read_only_fields = ["id"]


class HostelEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = HostelEvent
        fields = [
            "id",
            "id",
            "hostel",
            "organizer",
            "title",
            "description",
            "event_type",
            "status",
            "event_date",
            "start_time",
            "end_time",
            "location",
            "max_participants",
            "current_participants",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class HostelEventParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = HostelEventParticipant
        fields = ["id", "id", "event", "student", "registered_at", "attended", "feedback_rating", "feedback_comment"]
        read_only_fields = ["id"]


class HostelEmergencyProtocolSerializer(serializers.ModelSerializer):
    class Meta:
        model = HostelEmergencyProtocol
        fields = [
            "id",
            "id",
            "hostel",
            "emergency_type",
            "title",
            "description",
            "procedures",
            "contacts",
            "assembly_point",
            "last_drill_date",
            "next_drill_date",
            "is_active",
            "document",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class HostelEmergencyDrillSerializer(serializers.ModelSerializer):
    class Meta:
        model = HostelEmergencyDrill
        fields = [
            "id",
            "id",
            "hostel",
            "protocol",
            "conducted_by",
            "status",
            "drill_date",
            "start_time",
            "end_time",
            "participants_count",
            "evaluation",
            "evacuation_time_minutes",
            "issues_identified",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class HostelFeePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = HostelFeePayment
        fields = [
            "id",
            "school",
            "id",
            "allocation",
            "hostel_fee",
            "status",
            "amount_due",
            "amount_paid",
            "late_fee",
            "discount",
            "payment_method",
            "transaction_id",
            "payment_date",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class HostelInspectionScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = HostelInspectionSchedule
        fields = [
            "id",
            "id",
            "hostel",
            "inspector",
            "frequency",
            "day_of_week",
            "time_of_day",
            "rooms_to_inspect",
            "checklist_items",
            "is_active",
            "last_inspection_date",
            "next_inspection_date",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class MessFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessFeedback
        fields = [
            "id",
            "id",
            "hostel",
            "student",
            "meal_type",
            "rating",
            "food_quality",
            "portion_size",
            "hygiene_rating",
            "liked_items",
            "disliked_items",
            "suggestions",
            "meal_date",
            "is_anonymous",
        ]
        read_only_fields = ["id", "created_at"]


class HostelAttendanceAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = HostelAttendanceAlert
        fields = [
            "id",
            "school",
            "id",
            "student",
            "hostel",
            "alert_type",
            "severity",
            "status",
            "alert_date",
            "description",
            "related_attendance",
            "acknowledged_by",
        ]
        read_only_fields = ["id", "created_at"]
