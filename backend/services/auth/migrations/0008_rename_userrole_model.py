# Generated manually: rename UserRole model -> UserRoleAssignment.
# The DB table (auth_user_roles) is unchanged, so this only alters Django state.

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("auth_service", "0007_ipgeolocationcache_permission_auditreportschedule_and_more"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="UserRole",
            new_name="UserRoleAssignment",
        ),
    ]
