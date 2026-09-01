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
            "on_delete",
            "name",
            "code",
            "gender",
            "status",
            "warden",
            "on_delete",
            "assistant_warden",
            "on_delete",
            "address",
            "phone",
            "total_floors",
            "rules",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class HostelRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = HostelRoom
        fields = [
            "id",
            "hostel",
            "on_delete",
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


class HostelAllocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = HostelAllocation
        fields = [
            "id",
            "id",
            "student",
            "on_delete",
            "room",
            "on_delete",
            "status",
            "check_in_date",
            "check_out_date",
            "fee_amount",
            "is_paid",
            "notes",
            "allocated_by",
            "on_delete",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class HostelFeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = HostelFee
        fields = [
            "id",
            "school",
            "id",
            "on_delete",
            "name",
            "hostel",
            "on_delete",
            "room_type",
            "amount",
            "billing_cycle",
            "includes_meals",
            "includes_laundry",
            "includes_wifi",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class HostelVisitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = HostelVisitor
        fields = [
            "id",
            "id",
            "hostel",
            "on_delete",
            "visitor_name",
            "phone",
            "id_proof",
            "student_visited",
            "on_delete",
            "purpose",
            "in_time",
            "out_time",
            "relationship",
            "checked_in_by",
            "on_delete",
            "notes",
        ]
        read_only_fields = ["id", "created_at"]


class RoomMaintenanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomMaintenance
        fields = [
            "id",
            "id",
            "room",
            "on_delete",
            "maintenance_type",
            "description",
            "status",
            "priority",
            "reported_by",
            "on_delete",
            "assigned_to",
            "on_delete",
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
            "on_delete",
            "date",
            "status",
            "check_in_time",
            "check_out_time",
            "is_in_campus",
            "recorded_by",
            "on_delete",
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
            "on_delete",
            "leave_type",
            "reason",
            "status",
            "from_date",
            "to_date",
            "total_days",
            "approved_by",
            "on_delete",
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
            "on_delete",
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
        fields = ["id", "id", "mess_menu", "on_delete", "allocation", "on_delete", "status", "recorded_at"]
        read_only_fields = ["id"]


class ComplaintManagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplaintManagement
        fields = [
            "id",
            "id",
            "hostel",
            "on_delete",
            "allocation",
            "on_delete",
            "complaint_type",
            "title",
            "description",
            "status",
            "priority",
            "assigned_to",
            "on_delete",
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
            "on_delete",
            "inspection_type",
            "status",
            "scheduled_date",
            "completed_date",
            "cleanliness_rating",
            "orderliness_rating",
            "condition_rating",
            "inspected_by",
            "on_delete",
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
            "on_delete",
            "room",
            "on_delete",
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
            "on_delete",
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
            "on_delete",
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
            "on_delete",
            "from_room",
            "on_delete",
            "to_room",
            "on_delete",
            "reason",
            "status",
            "approved_by",
            "on_delete",
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
            "on_delete",
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
            "on_delete",
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
            "on_delete",
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
            "on_delete",
            "allocation",
            "on_delete",
            "feedback_type",
            "rating",
            "title",
            "comment",
            "suggestion",
            "is_anonymous",
            "response",
            "responded_by",
            "on_delete",
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
            "on_delete",
            "on_delete",
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
        fields = [
            "id",
            "id",
            "room",
            "on_delete",
            "student",
            "on_delete",
            "allocation",
            "on_delete",
            "match_score",
            "assigned_date",
            "is_active",
            "notes",
        ]
        read_only_fields = ["id"]


class RoomKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomKey
        fields = [
            "id",
            "id",
            "room",
            "on_delete",
            "key_number",
            "status",
            "allocated_to",
            "on_delete",
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
            "on_delete",
            "allocation",
            "on_delete",
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
            "on_delete",
            "student",
            "on_delete",
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
            "on_delete",
            "student",
            "on_delete",
            "allocation",
            "on_delete",
            "checked_by",
            "on_delete",
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
            "on_delete",
            "hostel",
            "on_delete",
            "resident",
            "on_delete",
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
            "on_delete",
            "requested",
            "on_delete",
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
            "on_delete",
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
            "on_delete",
            "student",
            "on_delete",
            "allocation",
            "on_delete",
            "diet_type",
            "status",
            "medical_reason",
            "doctor_note",
            "start_date",
            "end_date",
            "approved_by",
            "on_delete",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class HostelAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = HostelAsset
        fields = [
            "id",
            "id",
            "room",
            "on_delete",
            "hostel",
            "on_delete",
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
            "on_delete",
            "from_room",
            "on_delete",
            "to_room",
            "on_delete",
            "transferred_by",
            "on_delete",
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
            "on_delete",
            "organizer",
            "on_delete",
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
        fields = [
            "id",
            "id",
            "event",
            "on_delete",
            "student",
            "on_delete",
            "registered_at",
            "attended",
            "feedback_rating",
            "feedback_comment",
        ]
        read_only_fields = ["id"]


class HostelEmergencyProtocolSerializer(serializers.ModelSerializer):
    class Meta:
        model = HostelEmergencyProtocol
        fields = [
            "id",
            "id",
            "hostel",
            "on_delete",
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
            "on_delete",
            "protocol",
            "on_delete",
            "conducted_by",
            "on_delete",
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
            "on_delete",
            "allocation",
            "on_delete",
            "hostel_fee",
            "on_delete",
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
            "on_delete",
            "inspector",
            "on_delete",
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
            "on_delete",
            "student",
            "on_delete",
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
            "on_delete",
            "student",
            "on_delete",
            "hostel",
            "on_delete",
            "alert_type",
            "severity",
            "status",
            "alert_date",
            "description",
            "related_attendance",
            "on_delete",
            "acknowledged_by",
        ]
        read_only_fields = ["id", "created_at"]
