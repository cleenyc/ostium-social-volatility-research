from __future__ import annotations

from pathlib import Path

import ostium_social_volatility.__main__ as cli
from ostium_social_volatility import pipeline


ROOT = Path(__file__).resolve().parents[1]
STUDY = ROOT / "configs" / "study.oil-hormuz.example.yaml"


def test_cli_accepts_validate_report_and_run_commands(monkeypatch):
    calls: list[tuple[str, list[str]]] = []

    def fake_validate(args: list[str]) -> int:
        calls.append(("validate", args))
        return 0

    def fake_report(args: list[str]) -> int:
        calls.append(("report", args))
        return 0

    def fake_run(args: list[str]) -> int:
        calls.append(("run", args))
        return 0

    monkeypatch.setattr(cli.validate, "main", fake_validate)
    monkeypatch.setattr(cli.pipeline, "report_main", fake_report)
    monkeypatch.setattr(cli.pipeline, "run_main", fake_run)

    assert cli.main(["validate", "--study", str(STUDY)]) == 0
    assert cli.main(["report", "--study", str(STUDY)]) == 0
    assert cli.main(["run", "--study", str(STUDY), "--mode", "cached"]) == 0
    assert calls == [
        ("validate", ["--study", str(STUDY)]),
        ("report", ["--study", str(STUDY)]),
        ("run", ["--study", str(STUDY), "--mode", "cached"]),
    ]


def test_report_command_regenerates_cached_outputs_and_validates():
    rc = pipeline.report_main(["--study", str(STUDY)])

    assert rc == 0
    assert (ROOT / "reports" / "ostium-oil-hormuz-event-study-v1_3.csv").exists()
    assert (ROOT / "reports" / "ostium-oil-hormuz-volatility-control-v1_4.csv").exists()


def test_run_cached_command_generates_and_validates_outputs():
    rc = pipeline.run_main(["--study", str(STUDY), "--mode", "cached"])

    assert rc == 0
