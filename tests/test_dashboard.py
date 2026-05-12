from __future__ import annotations

import json
from pathlib import Path

from ostium_social_volatility.dashboard import build_dashboard_bundle

ROOT = Path(__file__).resolve().parents[1]
STUDY = ROOT / "configs" / "study.oil-hormuz.example.yaml"


def test_dashboard_bundle_contains_static_dashboard_summary_and_core_counts(tmp_path: Path):
    out_dir = tmp_path / "dashboard" / "data"

    payload = build_dashboard_bundle(STUDY, out_dir)

    assert payload["component"] == "Static dashboard"
    assert payload["included_components"][0] == "Research report package"
    assert payload["included_components"][-1] == "Optional live monitoring/recommendations"
    assert payload["study"]["id"] == "oil_hormuz"
    assert payload["event_study"]["post_count"] == 29
    assert payload["event_study"]["unique_dates"] == 21
    assert payload["event_study"]["total_impressions"] == 3744063
    assert len(payload["event_study"]["posts"]) == 29
    assert payload["volatility_control"]["row_count"] == 101
    assert len(payload["volatility_control"]["days"]) == 101
    assert payload["assumptions"]["primary_event_window"] == "0-2d"
    assert payload["assumptions"]["calendar_baseline_days"] == 30
    assert payload["volatility_control"]["high_vol_rows"] == 30
    assert payload["volatility_control"]["markets"]["WTI"]["eligible_days"] == 75
    assert payload["volatility_control"]["markets"]["BRENT"]["eligible_days"] == 26
    assert (out_dir / "summary.json").exists()
    written = json.loads((out_dir / "summary.json").read_text())
    assert written["event_study"]["post_count"] == 29


def test_dashboard_bundle_redacts_full_post_text_by_default(tmp_path: Path):
    payload = build_dashboard_bundle(STUDY, tmp_path)

    first = payload["event_study"]["top_social_posts"][0]
    assert "url" in first
    assert "text" not in first
    assert "text_summary" in first


def test_dashboard_bundle_embeds_report_sections_and_downloads(tmp_path: Path):
    payload = build_dashboard_bundle(STUDY, tmp_path)

    headings = [section["heading"] for section in payload["report"]["sections"]]
    assert "Executive Summary" in headings
    assert "Methodology Evolution" in headings
    assert "Research Report Package Conclusion" in headings
    downloads = {item["label"]: item["href"] for item in payload["dashboard_downloads"]}
    assert downloads["Research report v1"].endswith("data/downloads/ostium-social-volatility-research-report-v1.md")
    assert downloads["v1.3 event-study CSV"].endswith("data/downloads/ostium-oil-hormuz-event-study-v1_3.csv")
    assert downloads["v1.4 volatility-control report"].endswith("data/downloads/ostium-oil-hormuz-volatility-control-v1_4.md")
    assert "Public report draft" not in downloads
    assert "Methodology appendix" not in downloads
    assert (tmp_path / "downloads" / "ostium-oil-hormuz-event-study-v1_3.csv").exists()


def test_dashboard_bundle_contains_chart_ready_market_summaries(tmp_path: Path):
    payload = build_dashboard_bundle(STUDY, tmp_path)

    wti = payload["volatility_control"]["markets"]["WTI"]
    assert wti["high_vol_post_days"] == 10
    assert wti["high_vol_no_post_days"] == 15
    assert round(wti["high_vol_post_activity"]["median_activity_lift_pct"], 1) == 74.0
    assert round(wti["high_vol_no_post_activity"]["median_activity_lift_pct"], 1) == -9.3
    assert round(wti["high_vol_post_activity"]["median_event_notional_per_day"] / 1_000_000, 1) == 35.9
    assert round(wti["high_vol_no_post_activity"]["median_event_notional_per_day"] / 1_000_000, 1) == 6.5

    wti_events = payload["event_study"]["market_summaries"]["WTI"]
    assert wti_events["positive_counts"]["range_0_2d"] == 18
    assert wti_events["positive_counts"]["activity_0_2d"] == 14
