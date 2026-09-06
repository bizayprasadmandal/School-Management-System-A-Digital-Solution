"""Cafeteria — School-scoped viewsets."""

from core.pagination import StandardResultsSetPagination
from core.permissions import IsSchoolAdmin, IsSchoolMember
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticated

from .models import (
    AllergenManagement,
    CafeteriaAlert,
    CafeteriaAnalytics,
    CafeteriaCapacity,
    CafeteriaEquipment,
    CafeteriaFeedback,
    CafeteriaHolidaySchedule,
    CafeteriaInventory,
    CafeteriaInventoryAlert,
    CafeteriaMonthlyReport,
    CafeteriaReservation,
    CafeteriaStaff,
    CashRegister,
    DailySalesSummary,
    DietaryRestriction,
    FoodSafetyCheck,
    FoodSafetyIncident,
    FreeReducedLunch,
    MealBooking,
    MealDelivery,
    MealMenu,
    MealPlan,
    MealPreOrder,
    MealSubscription,
    MenuItemAllergen,
    MenuItemRating,
    NutritionAnalysis,
    NutritionTracking,
    OnlineOrder,
    OnlineOrderItem,
    PaymentTransaction,
    PointOfSale,
    PreOrderSystem,
    ProductionPlanning,
    StudentAccount,
    SubscriptionUsage,
    USDAComplianceReport,
    VendorManagement,
    VendorOrder,
    WasteTracking,
)
from .serializers import (
    AllergenManagementSerializer,
    CafeteriaAlertSerializer,
    CafeteriaAnalyticsSerializer,
    CafeteriaCapacitySerializer,
    CafeteriaEquipmentSerializer,
    CafeteriaFeedbackSerializer,
    CafeteriaHolidayScheduleSerializer,
    CafeteriaInventoryAlertSerializer,
    CafeteriaInventorySerializer,
    CafeteriaMonthlyReportSerializer,
    CafeteriaReservationSerializer,
    CafeteriaStaffSerializer,
    CashRegisterSerializer,
    DailySalesSummarySerializer,
    DietaryRestrictionSerializer,
    FoodSafetyCheckSerializer,
    FoodSafetyIncidentSerializer,
    FreeReducedLunchSerializer,
    MealBookingSerializer,
    MealDeliverySerializer,
    MealMenuSerializer,
    MealPlanSerializer,
    MealPreOrderSerializer,
    MealSubscriptionSerializer,
    MenuItemAllergenSerializer,
    MenuItemRatingSerializer,
    NutritionAnalysisSerializer,
    NutritionTrackingSerializer,
    OnlineOrderItemSerializer,
    OnlineOrderSerializer,
    PaymentTransactionSerializer,
    PointOfSaleSerializer,
    PreOrderSystemSerializer,
    ProductionPlanningSerializer,
    StudentAccountSerializer,
    SubscriptionUsageSerializer,
    USDAComplianceReportSerializer,
    VendorManagementSerializer,
    VendorOrderSerializer,
    WasteTrackingSerializer,
)


class MealMenuViewSet(viewsets.ModelViewSet):
    serializer_class = MealMenuSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name", "items", "description"]
    filterset_fields = ["meal_type", "date", "is_active"]

    def get_queryset(self):
        return MealMenu.objects.filter(school=self.request.user.school).annotate(booking_count=Count("bookings"))

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class MealPlanViewSet(viewsets.ModelViewSet):
    serializer_class = MealPlanSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name", "description"]
    filterset_fields = ["is_active"]

    def get_queryset(self):
        return MealPlan.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class MealBookingViewSet(viewsets.ModelViewSet):
    serializer_class = MealBookingSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["user__first_name", "user__last_name", "menu__name"]
    filterset_fields = ["meal_type", "status", "menu", "booking_date"]

    def get_queryset(self):
        return MealBooking.objects.filter(school=self.request.user.school).select_related("user", "menu", "meal_plan")

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class DietaryRestrictionViewSet(viewsets.ModelViewSet):
    serializer_class = DietaryRestrictionSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["user", "restriction_type"]

    def get_queryset(self):
        return DietaryRestriction.objects.filter(user__school=self.request.user.school).select_related("user")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()


class PointOfSaleViewSet(viewsets.ModelViewSet):
    serializer_class = PointOfSaleSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["user", "transaction_type", "payment_method", "benefit_type"]

    def get_queryset(self):
        return PointOfSale.objects.filter(school=self.request.user.school).select_related("user", "menu")

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class PaymentTransactionViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentTransactionSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["user", "transaction_type", "payment_method", "status"]

    def get_queryset(self):
        return PaymentTransaction.objects.filter(school=self.request.user.school).select_related(
            "user", "meal_plan", "booking"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class FreeReducedLunchViewSet(viewsets.ModelViewSet):
    serializer_class = FreeReducedLunchSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["student", "eligibility_type", "status"]

    def get_queryset(self):
        return FreeReducedLunch.objects.filter(school=self.request.user.school).select_related(
            "student__user", "reviewed_by"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolAdmin()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class CafeteriaInventoryViewSet(viewsets.ModelViewSet):
    serializer_class = CafeteriaInventorySerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["category", "is_perishable", "is_active"]

    def get_queryset(self):
        return CafeteriaInventory.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolAdmin()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class USDAComplianceReportViewSet(viewsets.ModelViewSet):
    serializer_class = USDAComplianceReportSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["report_type", "status"]

    def get_queryset(self):
        return USDAComplianceReport.objects.filter(school=self.request.user.school).select_related(
            "submitted_by", "approved_by"
        )

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolAdmin()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class PreOrderSystemViewSet(viewsets.ModelViewSet):
    serializer_class = PreOrderSystemSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["user", "menu", "status", "payment_status"]

    def get_queryset(self):
        return PreOrderSystem.objects.filter(school=self.request.user.school).select_related("user", "menu")

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class StudentAccountViewSet(viewsets.ModelViewSet):
    serializer_class = StudentAccountSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["user", "status", "auto_replenish_enabled"]

    def get_queryset(self):
        return StudentAccount.objects.filter(school=self.request.user.school).select_related("user")

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class AllergenManagementViewSet(viewsets.ModelViewSet):
    serializer_class = AllergenManagementSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["severity", "is_active"]

    def get_queryset(self):
        return AllergenManagement.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolAdmin()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class MenuItemAllergenViewSet(viewsets.ModelViewSet):
    serializer_class = MenuItemAllergenSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["menu", "allergen"]

    def get_queryset(self):
        return MenuItemAllergen.objects.filter(menu__school=self.request.user.school).select_related("menu", "allergen")

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolAdmin()]

    def perform_create(self, serializer):
        serializer.save()


class NutritionTrackingViewSet(viewsets.ModelViewSet):
    serializer_class = NutritionTrackingSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["user", "date"]

    def get_queryset(self):
        return NutritionTracking.objects.filter(school=self.request.user.school).select_related("user")

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class VendorManagementViewSet(viewsets.ModelViewSet):
    serializer_class = VendorManagementSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status"]

    def get_queryset(self):
        return VendorManagement.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolAdmin()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class VendorOrderViewSet(viewsets.ModelViewSet):
    serializer_class = VendorOrderSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["vendor", "status", "payment_status"]

    def get_queryset(self):
        return VendorOrder.objects.filter(school=self.request.user.school).select_related("vendor", "created_by")

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolAdmin()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, created_by=self.request.user)


class ProductionPlanningViewSet(viewsets.ModelViewSet):
    serializer_class = ProductionPlanningSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["menu", "status"]

    def get_queryset(self):
        return ProductionPlanning.objects.filter(school=self.request.user.school).select_related("menu", "assigned_to")

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolAdmin()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class WasteTrackingViewSet(viewsets.ModelViewSet):
    serializer_class = WasteTrackingSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["waste_type", "date"]

    def get_queryset(self):
        return WasteTracking.objects.filter(school=self.request.user.school).select_related("menu", "recorded_by")

    def get_permissions(self):
        return [IsAuthenticated(), IsSchoolAdmin()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school, recorded_by=self.request.user)


# ── Additional ViewSets (module expansion) ──


class OnlineOrderViewSet(viewsets.ModelViewSet):
    serializer_class = OnlineOrderSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return OnlineOrder.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class OnlineOrderItemViewSet(viewsets.ModelViewSet):
    serializer_class = OnlineOrderItemSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return OnlineOrderItem.objects.filter(order__school=self.request.user.school).select_related(
            "order", "menu_item"
        )

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()


class MealDeliveryViewSet(viewsets.ModelViewSet):
    serializer_class = MealDeliverySerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return MealDelivery.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class CashRegisterViewSet(viewsets.ModelViewSet):
    serializer_class = CashRegisterSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return CashRegister.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class DailySalesSummaryViewSet(viewsets.ModelViewSet):
    serializer_class = DailySalesSummarySerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return DailySalesSummary.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class FoodSafetyCheckViewSet(viewsets.ModelViewSet):
    serializer_class = FoodSafetyCheckSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return FoodSafetyCheck.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class FoodSafetyIncidentViewSet(viewsets.ModelViewSet):
    serializer_class = FoodSafetyIncidentSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return FoodSafetyIncident.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class CafeteriaStaffViewSet(viewsets.ModelViewSet):
    serializer_class = CafeteriaStaffSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return CafeteriaStaff.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class CafeteriaFeedbackViewSet(viewsets.ModelViewSet):
    serializer_class = CafeteriaFeedbackSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return CafeteriaFeedback.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class MealPreOrderViewSet(viewsets.ModelViewSet):
    serializer_class = MealPreOrderSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return MealPreOrder.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class NutritionAnalysisViewSet(viewsets.ModelViewSet):
    serializer_class = NutritionAnalysisSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return NutritionAnalysis.objects.filter(menu_item__school=self.request.user.school).select_related("menu_item")

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(analyzed_by=self.request.user)


class CafeteriaEquipmentViewSet(viewsets.ModelViewSet):
    serializer_class = CafeteriaEquipmentSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["name"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return CafeteriaEquipment.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class CafeteriaReservationViewSet(viewsets.ModelViewSet):
    serializer_class = CafeteriaReservationSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return CafeteriaReservation.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class CafeteriaAlertViewSet(viewsets.ModelViewSet):
    serializer_class = CafeteriaAlertSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return CafeteriaAlert.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class MealSubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = MealSubscriptionSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return MealSubscription.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class SubscriptionUsageViewSet(viewsets.ModelViewSet):
    serializer_class = SubscriptionUsageSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return SubscriptionUsage.objects.filter(subscription__school=self.request.user.school).select_related(
            "subscription", "menu_item"
        )

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()


class CafeteriaAnalyticsViewSet(viewsets.ModelViewSet):
    serializer_class = CafeteriaAnalyticsSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return CafeteriaAnalytics.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class CafeteriaCapacityViewSet(viewsets.ModelViewSet):
    serializer_class = CafeteriaCapacitySerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return CafeteriaCapacity.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class MenuItemRatingViewSet(viewsets.ModelViewSet):
    serializer_class = MenuItemRatingSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]

    def get_queryset(self):
        return MenuItemRating.objects.filter(menu_item__school=self.request.user.school).select_related(
            "menu_item", "student"
        )

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save()


class CafeteriaHolidayScheduleViewSet(viewsets.ModelViewSet):
    serializer_class = CafeteriaHolidayScheduleSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return CafeteriaHolidaySchedule.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class CafeteriaMonthlyReportViewSet(viewsets.ModelViewSet):
    serializer_class = CafeteriaMonthlyReportSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return CafeteriaMonthlyReport.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)


class CafeteriaInventoryAlertViewSet(viewsets.ModelViewSet):
    serializer_class = CafeteriaInventoryAlertSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["id"]
    filterset_fields = ["school"]

    def get_queryset(self):
        return CafeteriaInventoryAlert.objects.filter(school=self.request.user.school)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsSchoolAdmin()]
        return [IsAuthenticated(), IsSchoolMember()]

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school)
