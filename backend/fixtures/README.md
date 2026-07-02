# Fixtures

This directory is for Django fixture files (`loaddata` format).

The recommended way to seed demo data is via the management command instead:
```bash
python manage.py seed_demo_data
```

This creates a complete demo school with 120 students, 8 teachers, fee structures,
notification templates, and sample announcements — far more realistic than a static
fixture file. See `services/auth/management/commands/seed_demo_data.py`.

If you need a static fixture (e.g. for CI smoke tests), generate one with:
```bash
python manage.py dumpdata auth_service students academics \
  --indent 2 > fixtures/demo_school.json
```
