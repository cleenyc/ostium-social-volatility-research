import csv
from pathlib import Path

from ostium_social_volatility.validate import load_simple_yaml, validate_study


ROOT = Path(__file__).resolve().parents[1]
STUDY = ROOT / "configs" / "study.oil-hormuz.example.yaml"


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def test_load_simple_yaml_parses_study_config():
    config = load_simple_yaml(STUDY)

    assert config["study"]["id"] == "oil_hormuz"
    assert config["markets"][0]["label"] == "WTI"
    assert config["markets"][1]["ostium_pair_id"] == 55
    assert config["validation"]["fixture_expectations"]["event_study"]["posts"] == 29
    assert config["validation"]["fixture_expectations"]["markets"][0]["label"] == "WTI"
    assert config["paths"]["reports"]["volatility_control_csv"].endswith("v1_4.csv")


def test_cached_study_validation_passes_current_artifacts():
    report = validate_study(STUDY)

    assert report.summary()["fail"] == 0
    assert any(c.name == "event_study_csv.posts" and c.level == "ok" for c in report.checks)
    assert any(c.name == "volatility_control.WTI.high_vol_days" and c.level == "ok" for c in report.checks)
    assert any(c.name == "volatility_control.WTI.high_vol_post_days" and c.level == "ok" for c in report.checks)
    assert any(c.name == "processed_control.matches_report_csv" and c.level == "ok" for c in report.checks)


def test_portable_new_market_validation_has_no_oil_fixture_counts(tmp_path: Path):
    repo = tmp_path
    (repo / "configs").mkdir()
    study = repo / "configs" / "study.copper.example.yaml"
    study.write_text(
        """
schema_version: 0.1
study:
  id: copper_test
markets:
  - label: COPPER
    ostium_builder_symbol: "HG-USD"
    ostium_pair_id: 99
paths:
  processed:
    posts: "data/processed/copper_posts.csv"
    volatility_control_days: "data/processed/volatility_control_days.csv"
  reports:
    event_study_csv: "reports/copper-event-study.csv"
    volatility_control_csv: "reports/copper-volatility-control.csv"
validation:
  required_outputs:
    - "reports/copper-event-study.csv"
    - "reports/copper-volatility-control.csv"
    - "data/processed/volatility_control_days.csv"
  public_safety:
    forbid_files:
      - ".env"
    forbid_path_patterns:
      - "token"
      - "secret"
""".strip()
    )
    event_rows = [
        {
            "tweet_id": "1",
            "url": "https://x.com/example/status/1",
            "created_at": "2026-01-01T00:00:00Z",
            "date_utc": "2026-01-01",
            "post_type": "original",
            "impressions": 100,
            "COPPER_range_event0_2_lift_pct": 12.5,
        }
    ]
    posts_rows = [
        {
            "tweet_id": "1",
            "created_at": "2026-01-01T00:00:00Z",
            "date_utc": "2026-01-01",
            "text": "copper test",
            "impressions": 100,
            "engagement_count": 5,
        }
    ]
    control_rows = [
        {
            "date_utc": "2026-01-01",
            "market": "COPPER",
            "range_lift_pct": 12.5,
            "range_percentile_vs_baseline": 80,
            "has_oil_post": "True",
            "oil_post_count": 1,
            "oil_original_count": 1,
            "activity_event0_2_lift_pct": 20,
        }
    ]
    write_csv(repo / "reports" / "copper-event-study.csv", event_rows)
    write_csv(repo / "data" / "processed" / "copper_posts.csv", posts_rows)
    write_csv(repo / "reports" / "copper-volatility-control.csv", control_rows)
    write_csv(repo / "data" / "processed" / "volatility_control_days.csv", control_rows)

    report = validate_study(study)
    names = {c.name for c in report.checks}

    assert report.summary()["fail"] == 0
    assert "volatility_control.COPPER.eligible_days" in names
    assert "volatility_control.COPPER.high_vol_days" in names
    assert "volatility_control.WTI.high_vol_days" not in names
    assert "volatility_control.BRENT.high_vol_days" not in names
    assert next(c for c in report.checks if c.name == "event_study_csv.posts").message == "observed 1 posts"
