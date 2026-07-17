"""
Fees Service — Serializers
"""

from rest_framework import serializers
from .models import FeeCategory, FeeStructure, FeeInvoice, Payment, Scholarship, PaymentGatewayConfig


class FeeCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeCategory
        fields = ["id", "name", "description", "is_mandatory", "is_recurring", "recurrence"]


class FeeStructureSerializer(serializers.ModelSerializer):
    grade_name = serializers.CharField(source="grade.name", read_only=True)
    category_name = serializers.CharField(source="fee_category.name", read_only=True)
    academic_year_name = serializers.CharField(source="academic_year.name", read_only=True)

    class Meta:
        model = FeeStructure
        fields = [
            "id", "grade", "grade_name", "fee_category", "category_name",
            "academic_year", "academic_year_name", "amount", "due_day",
            "late_fee_per_day", "is_active",
        ]


class FeeInvoiceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    student_admission_number = serializers.CharField(source="student.admission_number", read_only=True)
    category_name = serializers.CharField(source="fee_structure.fee_category.name", read_only=True)
    outstanding_amount = serializers.ReadOnlyField()
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = FeeInvoice
        fields = [
            "id", "invoice_number", "student", "student_name",
            "student_admission_number", "academic_year", "fee_structure",
            "category_name", "due_date", "base_amount", "discount_amount",
            "late_fee", "total_amount", "paid_amount", "outstanding_amount",
            "status", "notes", "created_at", "is_overdue",
        ]
        read_only_fields = [
            "id", "invoice_number", "outstanding_amount", "created_at",
        ]

    def get_is_overdue(self, obj):
        from django.utils import timezone
        return (
            obj.status in ["unpaid", "partial"]
            and obj.due_date < timezone.now().date()
        )

    def create(self, validated_data):
        import uuid
        validated_data["invoice_number"] = f"INV-{uuid.uuid4().hex[:8].upper()}"
        return super().create(validated_data)


class PaymentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="invoice.student.user.full_name", read_only=True)
    student_admission_number = serializers.CharField(source="invoice.student.admission_number", read_only=True)
    invoice_number = serializers.CharField(source="invoice.invoice_number", read_only=True)
    collected_by_name = serializers.CharField(source="collected_by.full_name", read_only=True, default=None)

    class Meta:
        model = Payment
        fields = [
            "id", "invoice", "invoice_number", "student_name",
            "student_admission_number", "amount", "payment_method",
            "status", "transaction_id", "gateway_response",
            "receipt_number", "paid_at", "collected_by_name",
            "notes", "created_at",
        ]
        read_only_fields = ["id", "receipt_number", "status", "paid_at", "created_at"]

    def create(self, validated_data):
        import uuid
        from django.utils import timezone
        validated_data["receipt_number"] = f"RCP-{uuid.uuid4().hex[:8].upper()}"
        validated_data["status"] = "successful"
        validated_data["paid_at"] = timezone.now()
        return super().create(validated_data)


class ScholarshipSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    approved_by_name = serializers.CharField(source="approved_by.full_name", read_only=True)

    class Meta:
        model = Scholarship
        fields = [
            "id", "student", "student_name", "academic_year",
            "name", "discount_type", "discount_value",
            "applies_to_categories", "reason",
            "approved_by", "approved_by_name", "is_active",
        ]
        read_only_fields = ["id", "approved_by"]


class PaymentGatewayConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentGatewayConfig
        fields = ["stripe_enabled", "khalti_enabled", "esewa_enabled"]
