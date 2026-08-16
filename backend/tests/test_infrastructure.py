"""
Infrastructure tasks — coverage for the daily PostgreSQL backup Celery task
(`create_database_backup`) and its retention pruning, verified without a real
PostgreSQL server by faking the shelled-out subprocesses.

Run standalone:

    python -m pytest tests/test_infrastructure.py -q
"""

import os
import time
from unittest import mock

import pytest
from celery.exceptions import Retry
from services.infrastructure import tasks

EXPECTED_PGDUMP_CMD = [
    "pg_dump",
    "-h",
    "dbhost",
    "-p",
    "5432",
    "-U",
    "dbuser",
    "-d",
    "dbname",
    "--no-owner",
    "--no-acl",
    "--format=plain",
]


class FakeProc:
    """Drop-in stand-in for subprocess.Popen used by the backup task."""

    def __init__(self, cmd, **kwargs):
        self.cmd = cmd
        self.returncode = 0
        self.stdout = kwargs.get("stdout")
        if self.stdout is not None:
            self.stdout.write(b"compressed-dump")
            self.stdout.flush()
        self.stdin = mock.MagicMock()

    def communicate(self):
        return (None, b"")

    def wait(self):
        return self.returncode


def _install_env(monkeypatch, tmp_path):
    monkeypatch.setattr(tasks, "BACKUP_DIR", str(tmp_path))
    monkeypatch.setenv("PGHOST", "dbhost")
    monkeypatch.setenv("PGPORT", "5432")
    monkeypatch.setenv("PGUSER", "dbuser")
    monkeypatch.setenv("PGPASSWORD", "secret")
    monkeypatch.setenv("PGDATABASE", "dbname")
    monkeypatch.setattr(tasks, "RETENTION_DAYS", 30)
    monkeypatch.setattr(tasks, "BACKUP_S3_BUCKET", "")
    monkeypatch.setattr(tasks, "BACKUP_S3_PREFIX", "")
    monkeypatch.setattr(tasks, "BACKUP_S3_REGION", "")


class TestCreateDatabaseBackup:
    def test_success_path(self, tmp_path, monkeypatch):
        _install_env(monkeypatch, tmp_path)
        procs = []

        def fake_popen(cmd, **kwargs):
            proc = FakeProc(cmd, **kwargs)
            procs.append(proc)
            return proc

        monkeypatch.setattr(tasks.subprocess, "Popen", fake_popen)

        result = tasks.create_database_backup.run()

        assert result["filename"].startswith("sms-daily-")
        assert result["filename"].endswith(".sql.gz")
        assert result["size_bytes"] > 0
        assert result["uploaded_to_s3"] is False
        assert result["pruned_count"] == 0

        files = os.listdir(tmp_path)
        assert len(files) == 1
        assert files[0] == result["filename"]

    def test_pg_dump_command_shape(self, tmp_path, monkeypatch):
        """The pg_dump invocation must match the documented convention so the
        monitoring/verification scripts can trust the produced dump."""
        _install_env(monkeypatch, tmp_path)
        procs = []

        def fake_popen(cmd, **kwargs):
            proc = FakeProc(cmd, **kwargs)
            procs.append(proc)
            return proc

        monkeypatch.setattr(tasks.subprocess, "Popen", fake_popen)

        tasks.create_database_backup.run()

        dump_calls = [p for p in procs if p.cmd[0] == "pg_dump"]
        assert len(dump_calls) == 1
        assert dump_calls[0].cmd == EXPECTED_PGDUMP_CMD

    def test_pg_dump_failure_raises_retry_and_cleans_up(self, tmp_path, monkeypatch):
        _install_env(monkeypatch, tmp_path)

        def fake_popen(cmd, **kwargs):
            proc = FakeProc(cmd, **kwargs)
            if cmd[0] != "gzip":
                proc.returncode = 1
                proc.communicate = lambda: (None, b"pg_dump: error: cannot connect")
            return proc

        monkeypatch.setattr(tasks.subprocess, "Popen", fake_popen)
        monkeypatch.setattr(tasks.create_database_backup, "retry", _raise_retry)

        with pytest.raises(Retry):
            tasks.create_database_backup.run()

        assert os.listdir(tmp_path) == []

    def test_subprocess_exception_raises_retry(self, tmp_path, monkeypatch):
        _install_env(monkeypatch, tmp_path)

        def boom_popen(cmd, **kwargs):
            raise OSError("pg_dump executable not found")

        monkeypatch.setattr(tasks.subprocess, "Popen", boom_popen)
        monkeypatch.setattr(tasks.create_database_backup, "retry", _raise_retry)

        with pytest.raises(Retry):
            tasks.create_database_backup.run()


def _raise_retry(exc=None, **kwargs):
    raise Retry(exc=exc)


class TestUploadToS3:
    def test_skipped_when_bucket_unset(self, tmp_path, monkeypatch):
        monkeypatch.setattr(tasks, "BACKUP_S3_BUCKET", "")
        assert (
            tasks._upload_to_s3(str(tmp_path / "sms-daily-20260101_000000.sql.gz"), "sms-daily-20260101_000000.sql.gz")
            is False
        )


class TestPruneOldBackups:
    def test_deletes_old_keeps_new(self, tmp_path, monkeypatch):
        monkeypatch.setattr(tasks, "BACKUP_DIR", str(tmp_path))
        monkeypatch.setattr(tasks, "RETENTION_DAYS", 30)

        old = tmp_path / "sms-daily-20200101_000000.sql.gz"
        old.write_bytes(b"old")
        old_ts = time.time() - 40 * 86400
        os.utime(old, (old_ts, old_ts))

        new = tmp_path / "sms-daily-20990101_000000.sql.gz"
        new.write_bytes(b"new")

        unrelated = tmp_path / "other.txt"
        unrelated.write_text("keep")

        assert tasks._prune_old_backups() == 1
        assert not old.exists()
        assert new.exists()
        assert unrelated.exists()

    def test_idempotent(self, tmp_path, monkeypatch):
        monkeypatch.setattr(tasks, "BACKUP_DIR", str(tmp_path))
        monkeypatch.setattr(tasks, "RETENTION_DAYS", 30)

        old = tmp_path / "sms-daily-20200101_000000.sql.gz"
        old.write_bytes(b"old")
        old_ts = time.time() - 40 * 86400
        os.utime(old, (old_ts, old_ts))

        assert tasks._prune_old_backups() == 1
        assert tasks._prune_old_backups() == 0

    def test_empty_dir(self, tmp_path, monkeypatch):
        monkeypatch.setattr(tasks, "BACKUP_DIR", str(tmp_path))
        monkeypatch.setattr(tasks, "RETENTION_DAYS", 30)
        assert tasks._prune_old_backups() == 0
