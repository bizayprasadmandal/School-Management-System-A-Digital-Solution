#!/bin/bash
# ─── Optimized Test Runner ─────────────────────────────────────────────────────
# Usage:
#   ./run_tests.sh                 # Run all tests in parallel
#   ./run_tests.sh --quick         # Skip slow tests (Axes lockout, email middleware)
#   ./run_tests.sh --file <file>   # Run a specific test file
#   ./run_tests.sh --module <name> # Run tests matching module name
# ────────────────────────────────────────────────────────────────────────────────

set -euo pipefail

CONTAINER="sms_backend"
APP_DIR="/app"

if [ "$#" -eq 0 ]; then
  echo "▶ Running ALL tests (drop -n for parallel, -m 'not slow' to skip slow)…"
  docker exec "$CONTAINER" sh -c "cd $APP_DIR && python -m pytest --timeout=120 2>&1 | tail -10"
  exit $?
fi

case "$1" in
  --quick)
    echo "▶ Running tests (excluding slow markers)…"
    shift
    docker exec "$CONTAINER" sh -c "cd $APP_DIR && python -m pytest --timeout=60 -q --tb=short --no-header -m 'not slow' $* 2>&1 | tail -10"
    ;;
  --file)
    shift
    FILE="$1"
    shift
    echo "▶ Running tests in: $FILE"
    docker exec "$CONTAINER" sh -c "cd $APP_DIR && python -m pytest -n auto --timeout=60 -q --tb=short $FILE $* 2>&1"
    ;;
  --module)
    shift
    MODULE="$1"
    shift
    echo "▶ Running tests matching: $MODULE"
    docker exec "$CONTAINER" sh -c "cd $APP_DIR && python -m pytest -n auto --timeout=60 -q --tb=short -k \"$MODULE\" tests/ $* 2>&1"
    ;;
  --slow)
    shift
    echo "▶ Running only slow tests (to isolate timeout issues)…"
    docker exec "$CONTAINER" sh -c "cd $APP_DIR && python -m pytest --timeout=300 -q --tb=long --no-header -m 'slow' $* 2>&1 | tail -20"
    ;;
  --list-slow)
    echo "▶ Listing tests marked as slow…"
    docker exec "$CONTAINER" sh -c "cd $APP_DIR && python -m pytest --co -q -m 'slow' 2>&1 | head -50"
    ;;
  --durations)
    echo "▶ Running all tests with duration reporting…"
    docker exec "$CONTAINER" sh -c "cd $APP_DIR && python -m pytest --timeout=120 -q --no-header --reuse-db --durations=10 2>&1 | tail -20"
    ;;
  --dry-run)
    echo "▶ Dry run — would execute: docker exec $CONTAINER python -m pytest [args]"
    shift
    docker exec "$CONTAINER" sh -c "cd $APP_DIR && python -m pytest --co -q $* 2>&1 | tail -3"
    ;;
  *)
    echo " ▶ Running with custom args: $*"
    docker exec "$CONTAINER" sh -c "cd $APP_DIR && python -m pytest $* 2>&1"
    ;;
esac
