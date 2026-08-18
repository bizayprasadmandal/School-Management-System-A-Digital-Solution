"""
Admissions tasks — expire overdue offers, run periodic housekeeping.
"""

import logging

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def expire_overdue_offers(self):
    """Cancel applications whose offer deadline has passed.

    Applications that were accepted (offer sent) but not accepted by the
    family before the deadline are moved to CANCELLED and a timeline event
    is recorded.  Runs daily via Celery Beat.
    """
    from .models import Application, ApplicationTimelineEvent

    today = timezone.now().date()

    try:
        expired = Application.objects.filter(
            status=Application.Status.ACCEPTED,
            offer_deadline__isnull=False,
            offer_deadline__lt=today,
            offer_accepted_at__isnull=True,
        )

        updated = 0
        for app in expired:
            app.status = Application.Status.CANCELLED
            app.review_notes = (
                f"{app.review_notes}\nOffer expired on {app.offer_deadline}."
                if app.review_notes
                else f"Offer expired on {app.offer_deadline}."
            )
            app.save(update_fields=["status", "review_notes"])
            ApplicationTimelineEvent.objects.create(
                application=app,
                stage=ApplicationTimelineEvent.Stage.STATUS_CHANGED,
                note=f"Offer expired (deadline was {app.offer_deadline})",
            )
            updated += 1

        logger.info(
            "expire_overdue_offers completed",
            extra={"expired_count": updated},
        )
        return {"expired": updated}
    except Exception as exc:
        logger.error("expire_overdue_offers failed: %s", exc)
        raise self.retry(exc=exc)
