"""
Auto-generated Django migration — Initial schema for auth_service
Run: python manage.py migrate
"""

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="School",
            fields=[
                ("id",     models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("name",   models.CharField(max_length=255)),
                ("code",   models.CharField(max_length=20, unique=True)),
                ("subdomain", models.CharField(max_length=63, unique=True)),
                ("logo",   models.ImageField(blank=True, null=True, upload_to="schools/logos/")),
                ("address", models.TextField()),
                ("phone",  models.CharField(max_length=20)),
                ("email",  models.EmailField()),
                ("website", models.URLField(blank=True)),
                ("timezone", models.CharField(default="UTC", max_length=50)),
                ("academic_year_start_month", models.PositiveSmallIntegerField(default=9)),
                ("is_active", models.BooleanField(default=True)),
                ("subscription_tier", models.CharField(
                    choices=[("basic","Basic"),("standard","Standard"),("premium","Premium")],
                    default="standard", max_length=20
                )),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"db_table": "schools"},
        ),
        migrations.CreateModel(
            name="User",
            fields=[
                ("password",  models.CharField(max_length=128, verbose_name="password")),
                ("last_login", models.DateTimeField(blank=True, null=True, verbose_name="last login")),
                ("is_superuser", models.BooleanField(default=False)),
                ("id",       models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("email",    models.EmailField(db_index=True, unique=True)),
                ("first_name", models.CharField(max_length=100)),
                ("last_name",  models.CharField(max_length=100)),
                ("phone",    models.CharField(blank=True, max_length=20)),
                ("avatar",   models.ImageField(blank=True, null=True, upload_to="users/avatars/")),
                ("role",     models.CharField(
                    choices=[
                        ("super_admin","Super Administrator"),("school_admin","School Administrator"),
                        ("teacher","Teacher"),("student","Student"),("parent","Parent / Guardian"),
                        ("accountant","Accountant"),("librarian","Librarian"),("counselor","Counselor"),
                    ],
                    db_index=True, max_length=20
                )),
                ("is_active", models.BooleanField(default=True)),
                ("is_staff",  models.BooleanField(default=False)),
                ("email_verified",       models.BooleanField(default=False)),
                ("two_factor_enabled",   models.BooleanField(default=False)),
                ("two_factor_secret",    models.CharField(blank=True, max_length=32)),
                ("last_login_ip",        models.GenericIPAddressField(blank=True, null=True)),
                ("date_joined",          models.DateTimeField(default=django.utils.timezone.now)),
                ("updated_at",           models.DateTimeField(auto_now=True)),
                ("notify_email",         models.BooleanField(default=True)),
                ("notify_sms",           models.BooleanField(default=False)),
                ("notify_push",          models.BooleanField(default=True)),
                ("school",   models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="users", to="auth_service.school"
                )),
                ("groups",   models.ManyToManyField(blank=True, related_name="user_set", to="auth.group")),
                ("user_permissions", models.ManyToManyField(blank=True, to="auth.permission")),
            ],
            options={"db_table": "users"},
        ),
        migrations.CreateModel(
            name="AuditLog",
            fields=[
                ("id",            models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ("action",        models.CharField(max_length=100)),
                ("resource_type", models.CharField(max_length=50)),
                ("resource_id",   models.CharField(blank=True, max_length=255)),
                ("changes",       models.JSONField(default=dict)),
                ("ip_address",    models.GenericIPAddressField(null=True)),
                ("user_agent",    models.TextField(blank=True)),
                ("timestamp",     models.DateTimeField(auto_now_add=True, db_index=True)),
                ("school", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="auth_service.school")),
                ("user",   models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to="auth_service.user")),
            ],
            options={"db_table": "audit_logs", "ordering": ["-timestamp"]},
        ),
        migrations.CreateModel(
            name="PasswordResetToken",
            fields=[
                ("id",         models.AutoField(primary_key=True)),
                ("token",      models.CharField(max_length=64, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("expires_at", models.DateTimeField()),
                ("used",       models.BooleanField(default=False)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="auth_service.user")),
            ],
            options={"db_table": "password_reset_tokens"},
        ),
        migrations.CreateModel(
            name="UserSession",
            fields=[
                ("id",               models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)),
                ("refresh_token_jti", models.CharField(max_length=255, unique=True)),
                ("device_info",      models.JSONField(default=dict)),
                ("ip_address",       models.GenericIPAddressField()),
                ("created_at",       models.DateTimeField(auto_now_add=True)),
                ("last_used",        models.DateTimeField(auto_now=True)),
                ("is_active",        models.BooleanField(default=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="sessions", to="auth_service.user")),
            ],
            options={"db_table": "user_sessions"},
        ),
        migrations.AddIndex(
            model_name="user",
            index=models.Index(fields=["school", "role"], name="users_school_role_idx"),
        ),
        migrations.AddIndex(
            model_name="user",
            index=models.Index(fields=["email", "is_active"], name="users_email_active_idx"),
        ),
    ]
