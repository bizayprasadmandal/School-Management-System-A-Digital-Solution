"""
Seed PaymentGatewayConfig rows for all existing schools.

Automatically creates a PaymentGatewayConfig entry with default values
(stripe_enabled=True, khalti_enabled=False, esewa_enabled=False) for every
school that doesn't already have one.
"""

from django.db import migrations


def seed_gateway_configs(apps, schema_editor):
    School = apps.get_model("auth_service", "School")
    PaymentGatewayConfig = apps.get_model("fees", "PaymentGatewayConfig")

    for school in School.objects.iterator():
        PaymentGatewayConfig.objects.get_or_create(
            school=school,
            defaults={
                "stripe_enabled": True,
                "khalti_enabled": False,
                "esewa_enabled": False,
            },
        )


def reverse_seed(apps, schema_editor):
    """Reverse: delete all PaymentGatewayConfig rows created by this migration."""
    PaymentGatewayConfig = apps.get_model("fees", "PaymentGatewayConfig")
    PaymentGatewayConfig.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("fees", "0003_payment_gateway_config"),
    ]

    operations = [
        migrations.RunPython(seed_gateway_configs, reverse_seed),
    ]
