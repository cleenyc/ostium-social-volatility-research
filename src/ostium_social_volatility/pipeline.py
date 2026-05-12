from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from ostium_social_volatility.validate import format_report, validate_study

REPO = Path(__file__).resolve().parents[2]
DEFAULT_STUDY = REPO / "configs" / "study.oil-hormuz.example.yaml"


def _run_script(script: str, study: Path) -> dict[str, object]:
    cmd = [sys.executable, str(REPO / "scripts" / script), "--study", str(study)]
    proc = subprocess.run(cmd, cwd=REPO, text=True, capture_output=True)
    if proc.returncode != 0:
        raise RuntimeError(
            f"{script} failed with exit code {proc.returncode}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        payload = {"stdout": proc.stdout.strip()}
    payload["script"] = script
    return payload


def rel(path: Path) -> str:
    try:
        return path.relative_to(REPO).as_posix()
    except ValueError:
        return path.as_posix()


def report(study: Path = DEFAULT_STUDY) -> dict[str, object]:
    study = study.resolve()
    outputs = [
        _run_script("run_event_study_report.py", study),
        _run_script("run_volatility_control_report.py", study),
    ]
    return {"study": rel(study), "reports": outputs}


def run_cached(study: Path = DEFAULT_STUDY, validate: bool = True) -> dict[str, object]:
    payload = report(study)
    if validate:
        validation = validate_study(study)
        payload["validation"] = validation.summary()
        if validation.failed:
            raise RuntimeError(format_report(validation))
    return payload


def report_main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Regenerate cached Ostium study reports from a study config.")
    parser.add_argument("--study", type=Path, default=DEFAULT_STUDY)
    args = parser.parse_args(argv)
    print(json.dumps(report(args.study), indent=2))
    return 0


def run_main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the Ostium study pipeline.")
    parser.add_argument("--study", type=Path, default=DEFAULT_STUDY)
    parser.add_argument("--mode", choices=["cached", "live"], default="cached")
    parser.add_argument("--no-validate", action="store_true", help="Skip validation after cached report generation")
    args = parser.parse_args(argv)
    if args.mode == "live":
        parser.error("live mode is intentionally not implemented in pipeline cleanup; run collectors explicitly after source-access review")
    print(json.dumps(run_cached(args.study, validate=not args.no_validate), indent=2))
    return 0
