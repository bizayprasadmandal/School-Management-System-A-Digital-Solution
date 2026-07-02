"""
Placeholder initial migration for the 'gradebook' service.

This file intentionally has empty operations. Run:
    python manage.py makemigrations gradebook
to generate the real migration from services/gradebook/models.py, then:
    python manage.py migrate
This stub exists only so the migrations package is importable before
that first makemigrations run.
"""
from django.db import migrations

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = []
