"""Guard: logger ``extra={...}`` dicts must not use reserved LogRecord names.

``logger.info("...", extra={"created": n})`` raises
``KeyError: Attempt to overwrite 'created' in LogRecord`` at logging time —
inside a Celery task that means the task fails and retries forever
(generate_bulk_invoices crash-looped exactly this way).

This suite statically parses every ``services/**/*.py`` file and asserts no
``extra=`` dict literal passes a reserved attribute name. String-concatenated
dict keys and ``**spread`` into extra are skipped (can't be verified
statically); the LogRecord reserved set is taken from
``logging.makeLogRecord`` documentation / ``logging.LogRecord.__init__``.
"""

import ast
import logging
from pathlib import Path

SERVICES_DIR = Path(__file__).resolve().parent.parent / "services"

# Attributes every LogRecord already carries — passing any of these via
# extra= collides with logging's own machinery. 'message' is only set on
# format() but is still reserved; 'asctime' is added by Formatter.
RESERVED = set(logging.LogRecord("x", logging.INFO, "p", 1, "m", None, None).__dict__.keys()) | {
    "taskName",  # added by logging in 3.12+; part of LogRecord on newer Pythons
    "asctime",  # added by Formatter, also reserved in practice
    "message",  # set during format(); passing it via extra= is clobbered
}

# Files we do not control (vendored snippets etc.) — none expected today.
SKIP_FILES: set[str] = set()


def _literal_dict_keys(call: ast.Call) -> list[tuple[str, int]]:
    """Static keys of the dict passed as extra=, plus their line numbers."""
    keys = []
    for kw in call.keywords:
        if kw.arg != "extra":
            continue
        if not isinstance(kw.value, ast.Dict):
            continue  # variable / call — not statically checkable
        for k in kw.value.keys:
            if isinstance(k, ast.Constant) and isinstance(k.value, str):
                keys.append((k.value, kw.value.lineno))
    return keys


def _iter_extra_calls(tree: ast.AST):
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and getattr(node.func, "attr", None) in {
            "debug",
            "info",
            "warning",
            "error",
            "exception",
            "critical",
            "log",
        }:
            yield node


def test_services_dir_exists():
    assert SERVICES_DIR.is_dir(), f"services dir not found at {SERVICES_DIR}"


def test_no_reserved_names_in_logger_extra():
    """No logger call may pass a reserved LogRecord attribute via extra=."""
    offenders = []
    files = sorted(SERVICES_DIR.rglob("*.py"))
    assert files, "no python files found under services/"

    for path in files:
        if path.name in SKIP_FILES:
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError:  # pragma: no cover
            continue
        for call in _iter_extra_calls(tree):
            for key, lineno in _literal_dict_keys(call):
                if key in RESERVED:
                    offenders.append(f"{path.relative_to(SERVICES_DIR.parent)}:{lineno} extra={key!r}")

    assert not offenders, (
        "logger extra= uses reserved LogRecord attribute(s) — these raise "
        "KeyError at logging time (crash-looping Celery tasks):\n  " + "\n  ".join(offenders)
    )


def test_reserved_set_is_sane():
    """Sanity: the reserved set actually contains the names that bit us."""
    assert "created" in RESERVED
    assert "message" in RESERVED
    assert "args" in RESERVED
