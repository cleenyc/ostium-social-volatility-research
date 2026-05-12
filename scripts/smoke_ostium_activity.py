#!/usr/bin/env python3
"""Run the Node-based Ostium SDK Phase 0 smoke test."""
import subprocess
from pathlib import Path

repo = Path(__file__).resolve().parents[1]
cmd = ["node", str(repo / "scripts" / "smoke_ostium_activity.mjs")]
raise SystemExit(subprocess.call(cmd, cwd=repo))
