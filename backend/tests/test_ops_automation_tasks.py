"""Tests for ops automation tasks: transport overdue/expiry, hostel overdue,
cafeteria low-stock alerts.

Each test pins transitions, dedup, and school scoping — the tasks run for
every school in one sweep, so cross-school isolation matters.
"""

from datetime import timedelta

import pytest
from django.utils import timezone
from tests.url_helpers import API_PREFIX  # noqa: F401


@pytest.fixture
def school(db):
    from tests.factories import SchoolFactory

    return SchoolFactory(code="OPS1")


@pytest.fixture
def other_school(db):
    from tests.factories import SchoolFactory

    return SchoolFactory(code="OPS2")


# ── Transportation ──────────────────────────────────────────────────────────


def _transport_fee(school, student, status="pending", due_offset_days=-3):
    from services.transportation.models import TransportFee

    return TransportFee.objects.create(
        school=school,
        student=student,
        fee_type=TransportFee.FeeType.MONTHLY,
        amount=1000,
        due_date=timezone.now().date() + timedelta(days=due_offset_days),
        status=status,
    )


@pytest.mark.django_db
class TestMarkOverdueTransportFees:
    def test_pending_past_due_flips_to_overdue(self, school, other_school):
        from services.transportation.tasks import mark_overdue_transport_fees
        from tests.factories import StudentFactory

        overdue = _transport_fee(school, StudentFactory(school=school), status="pending", due_offset_days=-5)
        future = _transport_fee(school, StudentFactory(school=school), status="pending", due_offset_days=10)
        paid = _transport_fee(school, StudentFactory(school=school), status="paid", due_offset_days=-5)
        # Other school's overdue fee must also flip (task is global) but counts separately
        other = _transport_fee(other_school, StudentFactory(school=other_school), status="pending", due_offset_days=-1)

        result = mark_overdue_transport_fees.apply().get()
        overdue.refresh_from_db()
        future.refresh_from_db()
        paid.refresh_from_db()
        other.refresh_from_db()

        assert overdue.status == "overdue"
        assert future.status == "pending"
        assert paid.status == "paid"
        assert other.status == "overdue"
        assert result["overdue_marked"] == 2

    def test_school_scoped_run(self, school, other_school):
        from services.transportation.tasks import mark_overdue_transport_fees
        from tests.factories import StudentFactory

        _transport_fee(school, StudentFactory(school=school), status="pending", due_offset_days=-5)
        _transport_fee(other_school, StudentFactory(school=other_school), status="pending", due_offset_days=-5)

        result = mark_overdue_transport_fees.apply(args=[school.id]).get()
        assert result["overdue_marked"] == 1


@pytest.mark.django_db
class TestTransportDocumentExpiry:
    def _license(self, school, expiry_offset_days):
        from services.transportation.models import Driver, DriverLicense

        driver = Driver.objects.create(school=school, full_name="Ram Bahadur")
        return DriverLicense.objects.create(
            driver=driver,
            license_number=f"LIC-{driver.id.hex[:8].upper()}",
            issue_date=timezone.now().date() - timedelta(days=365),
            expiry_date=timezone.now().date() + timedelta(days=expiry_offset_days),
        )

    def _insurance(self, school, end_offset_days):
        from services.transportation.models import Vehicle, VehicleInsurance

        vehicle = Vehicle.objects.create(
            school=school, plate_number=f"BA-{vehicle_seq()}PA", vehicle_type="bus", capacity=30
        )
        return VehicleInsurance.objects.create(
            vehicle=vehicle,
            policy_number=f"POL-{vehicle.id.hex[:8].upper()}",
            insurance_type="comprehensive",
            start_date=timezone.now().date() - timedelta(days=30),
            end_date=timezone.now().date() + timedelta(days=end_offset_days),
        )

    def test_expiring_license_and_insurance_notify_admins_once(self, school, other_school):
        from services.communication.models import Notification
        from services.transportation.tasks import check_transport_document_expiry
        from tests.factories import AdminUserFactory

        AdminUserFactory(school=school)
        lic = self._license(school, expiry_offset_days=10)
        ins = self._insurance(school, end_offset_days=3)

        r1 = check_transport_document_expiry.apply().get()
        assert r1["alerts_sent"] == 2  # 1 license + 1 insurance
        assert Notification.objects.filter(reference_type="driver_license", reference_id=str(lic.id)).count() == 1
        assert Notification.objects.filter(reference_type="vehicle_insurance", reference_id=str(ins.id)).count() == 1

        # Re-run: dedup — no new notifications
        r2 = check_transport_document_expiry.apply().get()
        assert r2["alerts_sent"] == 0
        assert Notification.objects.count() == 2

    def test_far_future_documents_are_ignored(self, school):
        from services.communication.models import Notification
        from services.transportation.tasks import check_transport_document_expiry

        self._license(school, expiry_offset_days=200)
        self._insurance(school, end_offset_days=120)
        check_transport_document_expiry.apply()
        assert Notification.objects.count() == 0


def vehicle_seq():
    counter = getattr(vehicle_seq, "_n", 0) + 1
    vehicle_seq._n = counter
    return f"{counter:02d}"


# ── Hostel ──────────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestMarkOverdueHostelPayments:
    def _payment(self, school, student, status="pending", due_offset_days=-4, name_suffix=""):
        from services.hostel.models import Hostel, HostelAllocation, HostelFeePayment, HostelRoom

        hostel, _ = Hostel.objects.get_or_create(school=school, name=f"Ops Hall{name_suffix}")
        room = HostelRoom.objects.create(hostel=hostel, room_number="OS1", capacity=2)
        allocation = HostelAllocation.objects.create(student=student, room=room, check_in_date=timezone.now().date())
        return HostelFeePayment.objects.create(
            school=school,
            allocation=allocation,
            amount_due=500,
            status=status,
            due_date=timezone.now().date() + timedelta(days=due_offset_days),
        )

    def test_pending_past_due_flips(self, school, other_school):
        from services.hostel.tasks import mark_overdue_hostel_payments
        from tests.factories import StudentFactory

        overdue = self._payment(school, StudentFactory(school=school), name_suffix="A")
        paid = self._payment(school, StudentFactory(school=school), status="paid", name_suffix="B")

        result = mark_overdue_hostel_payments.apply().get()
        overdue.refresh_from_db()
        paid.refresh_from_db()
        assert overdue.status == "overdue"
        assert paid.status == "paid"
        assert result["overdue_marked"] >= 1

    def test_school_scoped_run(self, school, other_school):
        from services.hostel.tasks import mark_overdue_hostel_payments
        from tests.factories import StudentFactory

        self._payment(school, StudentFactory(school=school), name_suffix="C")
        self._payment(other_school, StudentFactory(school=other_school), name_suffix="D")

        result = mark_overdue_hostel_payments.apply(args=[school.id]).get()
        assert result["overdue_marked"] == 1


# ── Cafeteria ───────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestCafeteriaLowStockAlerts:
    def _item(self, school, quantity, minimum=10):
        from services.cafeteria.models import CafeteriaInventory

        return CafeteriaInventory.objects.create(
            school=school,
            name=f"Rice {quantity}-{minimum}",
            category="grains",
            unit="kg",
            quantity=quantity,
            minimum_stock=minimum,
        )

    def test_low_and_out_of_stock_alerts(self, school, other_school):
        from services.cafeteria.models import CafeteriaInventoryAlert
        from services.cafeteria.tasks import generate_low_stock_alerts
        from tests.factories import AdminUserFactory

        AdminUserFactory(school=school)
        low = self._item(school, quantity=5, minimum=10)
        out = self._item(school, quantity=0, minimum=10)
        ok = self._item(school, quantity=50, minimum=10)

        r = generate_low_stock_alerts.apply().get()
        low.refresh_from_db()

        alert_low = CafeteriaInventoryAlert.objects.get(item=low)
        assert alert_low.alert_type == "low_stock"
        alert_out = CafeteriaInventoryAlert.objects.get(item=out)
        assert alert_out.alert_type == "out_of_stock"
        assert not CafeteriaInventoryAlert.objects.filter(item=ok).exists()
        assert r["alerts_created"] >= 2

    def test_dedup_on_rerun(self, school):
        from services.cafeteria.models import CafeteriaInventoryAlert
        from services.cafeteria.tasks import generate_low_stock_alerts

        item = self._item(school, quantity=5, minimum=10)
        generate_low_stock_alerts.apply()
        r2 = generate_low_stock_alerts.apply().get()
        assert CafeteriaInventoryAlert.objects.filter(item=item).count() == 1
        assert r2["alerts_created"] == 0
