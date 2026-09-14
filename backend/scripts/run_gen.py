"""Run gen_ui_configs with routes loaded from cluster_routes.json."""

import json
import subprocess
import sys

routes = json.load(open("scripts/cluster_routes.json", encoding="utf-8"))
out = subprocess.run(
    [sys.executable, "-X", "utf8", "scripts/gen_ui_configs.py", json.dumps(routes)],
    capture_output=True,
    text=True,
)
sys.stdout.write(out.stdout)
sys.stderr.write(out.stderr)
