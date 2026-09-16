"""Cafeteria Service — automated maintenance tasks.

Daily beat tasks:
- ``generate_low_stock_alerts``: inventory items at or below their minimum
  stock get an ACTIVE CafeteriaInventoryAlert (deduplicated — an existing
  ACTIVE low_stock alert for the item is reused, never duplicated).
"""

import logging

from celery import shared_task
from django.db.models import F, Q

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def generate_low_stock_alerts(self, school_id=None):
    """Create/renew low-stock alerts for cafeteria inventory items."""
    from services.cafeteria.models import CafeteriaInventory, CafeteriaInventoryAlert

    qs = CafeteriaInventory.objects.filter(
        Q(quantity__lte=F("minimum_stock")),
    )
    if school_id is not None:
        qs = qs.filter(school_id=school_id)

    created = 0
    for item in qs:
        out_of_stock = item.quantity <= 0
        alert_type = (
            CafeteriaInventoryAlert.AlertType.OUT_OF_STOCK
            if out_of_stock
            else CafeteriaInventoryAlert.AlertType.LOW_STOCK
        )
        message = (
            f"{item.name} is out of stock (0 {item.unit})."
            if out_of_stock
            else f"{item.name} is low: {item.quantity} {item.unit} " f"(minimum {item.minimum_stock} {item.unit})."
        )
        obj, was_created = CafeteriaInventoryAlert.objects.get_or_create(
            item=item,
            alert_type=alert_type,
            status=CafeteriaInventoryAlert.Status.ACTIVE,
            defaults={
                "school": item.school,
                "message": message,
                "current_quantity": item.quantity,
                "reorder_quantity": item.minimum_stock,
            },
        )
        if was_created:
            created += 1
        elif obj.current_quantity != item.quantity:
            # Keep the standing alert's snapshot fresh without spamming.
            obj.current_quantity = item.quantity
            obj.message = message
            obj.save(update_fields=["current_quantity", "message"])

    logger.info("generate_low_stock_alerts completed", extra={"alerts_created": created})
    return {"alerts_created": created}
