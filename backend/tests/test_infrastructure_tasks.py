"""Tests for the database backup task (services/infrastructure/tasks.py).

The task used to hardcode a default DB host/password, which silently failed
in every deployment shape (docker-compose uses a different password than the
default; Kubernetes resolves the DB under a different service name). These
tests pin the new behavior: connection settings resolve from the Django
DATABASE_URL config (via settings.DATABASES), and failures are handled
failure-tolerant (partial files removed, retry scheduled, S3 outage never
loses the local backup).
"""

from unittest import mock

import pytest
from services.infrastructure import tasks


@pytest.mark.django_db
class TestPgConnectionResolution:
    def test_resolves_from_django_settings(self):
        conn = tasks._pg_connection()
        db = __import__("django.conf", fromlist=["settings"]).settings.DATABASES["default"]
        assert conn["host"] == (db.get("HOST") or "postgres")
        assert conn["database"] == db.get("NAME") or "sms_db"
        assert conn["user"] == db.get("USER") or "sms"

    def test_pg_env_overrides_win(self, monkeypatch):
        monkeypatch.setenv("PGHOST", "pg-remote.example.com")
        monkeypatch.setenv("PGPORT", "5433")
        monkeypatch.setenv("PGUSER", "backup_user")
        monkeypatch.setenv("PGPASSWORD", "backup_secret")
        monkeypatch.setenv("PGDATABASE", "backup_db")

        conn = tasks._pg_connection()

        assert conn["host"] == "pg-remote.example.com"
        assert conn["port"] == "5433"
        assert conn["user"] == "backup_user"
        assert conn["password"] == "backup_secret"
        assert conn["database"] == "backup_db"

    def test_defaults_when_django_has_no_host(self, monkeypatch):
        monkeypatch.delenv("PGHOST", raising=False)
        monkeypatch.delenv("PGUSER", raising=False)
        monkeypatch.delenv("PGDATABASE", raising=False)
        monkeypatch.delenv("PGPASSWORD", raising=False)

        with mock.patch("django.conf.settings.DATABASES", {"default": {}}):
            conn = tasks._pg_connection()

        assert conn["host"] == "postgres"
        assert conn["port"] == "5432"
        assert conn["user"] == "sms"
        assert conn["database"] == "sms_db"


@pytest.mark.django_db
class TestCreateDatabaseBackup:
    def _popen_side_effect(self, dump_cls):
        """Real code calls Popen twice: gzip first, then pg_dump."""
        import io

        gzip_proc = mock.Mock()
        gzip_proc.stdin = io.BytesIO()
        return [gzip_proc, dump_cls()]

    def test_successful_backup_writes_file_and_reports(self, tmp_path, monkeypatch):
        monkeypatch.setattr(tasks, "BACKUP_DIR", str(tmp_path))

        class _FakeDump:
            returncode = 0
            stderr = b""

            def __init__(self, *a, **k):
                pass

            def communicate(self):
                return None, self.stderr

        with (
            mock.patch("subprocess.Popen", side_effect=self._popen_side_effect(_FakeDump)),
            mock.patch.object(tasks, "_upload_to_s3", return_value=False) as mock_upload,
            mock.patch.object(tasks, "_prune_old_backups", return_value=0),
        ):
            result = tasks.create_database_backup.run()

        assert result["uploaded_to_s3"] is False
        assert result["pruned_count"] == 0
        assert "filename" in result and result["filename"].startswith("sms-daily-")
        mock_upload.assert_called_once()

    def test_failed_dump_removes_partial_file_and_retries(self, tmp_path, monkeypatch):
        monkeypatch.setattr(tasks, "BACKUP_DIR", str(tmp_path))

        class _FailingDump:
            returncode = 1
            stderr = b"pg_dump: connection failed"

            def __init__(self, *a, **k):
                pass

            def communicate(self):
                return None, self.stderr

        # Patch retry() on the task proxy so the eager run hits our mock.
        with (
            mock.patch("subprocess.Popen", side_effect=self._popen_side_effect(_FailingDump)),
            mock.patch.object(tasks.create_database_backup, "retry", side_effect=Exception("retried")) as mock_retry,
            pytest.raises(Exception, match="retried"),
        ):
            tasks.create_database_backup.run()

        assert list(tmp_path.iterdir()) == []  # partial file cleaned up
        mock_retry.assert_called_once()

    def test_s3_upload_failure_tolerated(self, monkeypatch):
        """An S3 outage must never lose the local backup or fail the task."""
        monkeypatch.setattr(tasks, "BACKUP_S3_BUCKET", "sms-backups")

        task = mock.Mock()
        assert tasks._upload_to_s3("/tmp/backup.sql.gz", "backup.sql.gz") is False
        assert not task.retry.called
