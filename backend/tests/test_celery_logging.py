"""
Test Suite — Celery worker structured logging (core/celery.py signal handlers)

Covers the @task_failure handler added for worker error observability:
- every failure emits one structured JSON line via the ``celery.task`` logger
  (fields: task, task_id, task_args/task_kwargs, retries, exc_info)
- sensitive kwargs (password, tokens, *_secret_key) are redacted
- the handler never raises — a receiver exception would propagate into
  Celery's task failure/retry path and corrupt it
"""

import json
import logging

import pytest
from celery import signals as celery_signals
from pythonjsonlogger import jsonlogger


def _json_capture_handler():
    """Handler that records each emitted record formatted as a JSON line."""

    class Capture(logging.Handler):
        def __init__(self):
            super().__init__()
            self.records = []

        def emit(self, record):
            self.records.append(self.format(record))

    handler = Capture()
    handler.setFormatter(jsonlogger.JsonFormatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
    return handler


class _TaskRequest:
    queue = "default"
    retries = 1


class _FailingTask:
    name = "services.fees.tasks.generate_bulk_invoices"
    request = _TaskRequest()


class _ExceptionInfo:
    """Minimal stand-in for celery's ExceptionInfo (exposes ``.exception``)."""

    def __init__(self, exc):
        self.exception = exc


@pytest.fixture
def task_failure_logger():
    """Attach a JSON capture handler to the celery.task logger, then detach."""
    # Import here (not at module scope): autodiscover_tasks needs the Django
    # app registry, which pytest-django fully initializes before fixtures run.
    import core.celery  # noqa: F401 — registers the signal handlers

    logger = logging.getLogger("celery.task")
    handler = _json_capture_handler()
    logger.addHandler(handler)
    yield logger, handler
    logger.removeHandler(handler)


@pytest.fixture
def failed_task_einfo():
    """An einfo stand-in wrapping a real exception (with traceback)."""
    try:
        raise ValueError("boom: invoice generation failed")
    except ValueError as exc:
        return _ExceptionInfo(exc)


class TestTaskFailureLogging:
    def test_task_failure_emits_structured_json_record(self, task_failure_logger, failed_task_einfo):
        _logger, handler = task_failure_logger

        celery_signals.task_failure.send(
            sender=_FailingTask(),
            task_id="abc-123",
            args=(42,),
            kwargs={"user_id": 7},
            retries=2,
            einfo=failed_task_einfo,
        )

        assert handler.records, "task_failure signal produced no log record"
        data = json.loads(handler.records[0])

        assert data["name"] == "celery.task"
        assert data["levelname"] == "ERROR"
        assert "generate_bulk_invoices" in data["message"]
        assert data["task"] == "services.fees.tasks.generate_bulk_invoices"
        assert data["task_id"] == "abc-123"
        assert data["task_args"] == "[42]"
        assert data["retries"] == 2, "signal retries kwarg must be used"
        assert "Traceback" in data["exc_info"], "exception traceback missing"

    def test_task_failure_redacts_sensitive_kwargs(self, task_failure_logger, failed_task_einfo):
        _logger, handler = task_failure_logger

        celery_signals.task_failure.send(
            sender=_FailingTask(),
            task_id="t-2",
            args=None,
            kwargs={
                "user_id": 7,
                "password": "hunter2",
                "stripe_secret_key": "sk_live_abc",
                "api_token": "tok_123",
                "monkey": "banana",
            },
            retries=0,
            einfo=failed_task_einfo,
        )

        assert handler.records
        task_kwargs = json.loads(handler.records[0])["task_kwargs"]

        assert "password='***'" in task_kwargs
        assert "stripe_secret_key='***'" in task_kwargs
        assert "api_token='***'" in task_kwargs
        assert "monkey=banana" in task_kwargs, "innocuous keys must stay visible"
        assert "hunter2" not in task_kwargs
        assert "sk_live_abc" not in task_kwargs
        assert "tok_123" not in task_kwargs

    def test_task_failure_handler_never_raises_on_hostile_args(self, task_failure_logger, failed_task_einfo):
        """Deep nesting / broken __str__ must be swallowed, not propagated.

        Deliberately has no assertion beyond "signal returned without
        raising" — a raising receiver would corrupt Celery's failure/retry
        path, which is the regression this guards against.
        """
        _logger, _ = task_failure_logger

        deep = {}
        cur = deep
        for _ in range(3000):
            cur["n"] = {}
            cur = cur["n"]

        class BrokenStr:
            def __str__(self):
                raise RuntimeError("bad __str__")

        # Must not raise: a raising receiver would corrupt the failure/retry path.
        celery_signals.task_failure.send(
            sender=_FailingTask(),
            task_id="hostile",
            args=(deep, BrokenStr()),
            kwargs={},
            retries=0,
            einfo=failed_task_einfo,
        )
