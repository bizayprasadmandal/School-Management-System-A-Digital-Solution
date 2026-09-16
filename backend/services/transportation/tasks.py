"""Transportation Service — automated maintenance tasks.

Daily beat tasks:
- ``mark_overdue_transport_fees``: pending transport fees past due flip to
  overdue (idempotent — only pending rows transition).
- ``check_transport_document_expiry``: driver licenses and vehicle
  insurance policies expiring within 30 days notify school admins once per
  document (deduplicated via the Notification reference fields).
"""

import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def mark_overdue_transport_fees(self, school_id=None):
    """Flip pending transport fees whose due date has passed to overdue."""
    from services.transportation.models import TransportFee

    today = timezone.now().date()
    qs = TransportFee.objects.filter(status=TransportFee.Status.PENDING, due_date__lt=today)
    if school_id is not None:
        qs = qs.filter(school_id=school_id)

    updated = qs.update(status=TransportFee.Status.OVERDUE)
    logger.info(
        "mark_overdue_transport_fees completed",
        extra={"overdue_marked": updated, "cutoff_date": str(today)},
    )
    return {"overdue_marked": updated}


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def check_transport_document_expiry(self, days_ahead=30, school_id=None):
    """Alert admins about driver licenses / vehicle insurances expiring soon.

    Deduplication: one in-app Notification per document per severity window,
    keyed on (reference_type, reference_id, title) so re-runs never spam.
    """
    from datetime import date

    from services.transportation.models import DriverLicense, VehicleInsurance

    today = date.today()
    horizon = today + timedelta(days=days_ahead)
    notified = 0

    licenses = DriverLicense.objects.filter(expiry_date__lte=horizon).select_related("driver__school")
    insurances = VehicleInsurance.objects.filter(end_date__lte=horizon).select_related("vehicle__school")
    if school_id is not None:
        licenses = licenses.filter(driver__school_id=school_id)
        insurances = insurances.filter(vehicle__school_id=school_id)

    for lic in licenses:
        school = lic.driver.school
        days_left = (lic.expiry_date - today).days
        title = "Driver License Expiring" if days_left > 0 else "Driver License Expired"
        created = _notify_school_admins(
            school=school,
            title=title,
            body=(
                f"License {lic.license_number} for driver "
                f"{lic.driver.full_name} expires {lic.expiry_date:%B %d, %Y}"
                + (f" ({days_left} days left)" if days_left > 0 else "")
                + "."
            ),
            reference_type="driver_license",
            reference_id=str(lic.id),
        )
        notified += created

    for ins in insurances:
        school = ins.vehicle.school
        days_left = (ins.end_date - today).days
        title = "Vehicle Insurance Expiring" if days_left > 0 else "Vehicle Insurance Expired"
        created = _notify_school_admins(
            school=school,
            title=title,
            body=(
                f"Policy {ins.policy_number} for vehicle "
                f"{ins.vehicle} expires {ins.end_date:%B %d, %Y}"
                + (f" ({days_left} days left)" if days_left > 0 else "")
                + "."
            ),
            reference_type="vehicle_insurance",
            reference_id=str(ins.id),
        )
        notified += created

    logger.info(
        "check_transport_document_expiry completed",
        extra={"alerts_sent": notified, "horizon_days": days_ahead},
    )
    return {"alerts_sent": notified}


def _notify_school_admins(*, school, title, body, reference_type, reference_id):
    """Create one in-app notification per school admin; idempotent per document."""
    from services.communication.models import Notification

    exists = Notification.objects.filter(
        reference_type=reference_type,
        reference_id=reference_id,
        title=title,
        channel="in_app",
    ).exists()
    if exists:
        return 0

    recipients = school.users.filter(role__in=["school_admin", "super_admin"], is_active=True)
    created = 0
    for user in recipients:
        Notification.objects.create(
            user=user,
            title=title,
            body=body,
            channel="in_app",
            status="sent",
            reference_type=reference_type,
            reference_id=reference_id,
        )
        created += 1
    return created
