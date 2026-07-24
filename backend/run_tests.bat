@echo off
REM Run pytest locally against Docker PostgreSQL
REM Usage: run_tests.bat [test_path]
REM        run_tests.bat tests/test_2fa.py
REM        run_tests.bat (runs all tests)

set DJANGO_SETTINGS_MODULE=core.settings.base
set DATABASE_URL=postgresql://sms:sms@localhost:5432/sms_db
set REDIS_URL=redis://localhost:6379/0
set SECRET_KEY=test-secret-key-not-for-production-use

python -m pytest %* -c pytest-local.ini --override-ini="DJANGO_SETTINGS_MODULE=core.settings.base"
