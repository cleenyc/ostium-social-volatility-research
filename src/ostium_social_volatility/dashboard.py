from __future__ import annotations

import csv
import json
import re
import shutil
from pathlib import Path
from statistics import median
from typing import Any

from ostium_social_volatility.validate import get_nested, load_simple_yaml, resolve_path, repo_root_for


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _int(value: Any) -> int:
    number = _float(value)
    return int(number) if number is not None else 0


def _bool(value: Any) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def _median(values: list[float | None]) -> float | None:
    clean = [v for v in values if v is not None]
    return float(median(clean)) if clean else None


def _pct_positive(values: list[float | None]) -> float | None:
    clean = [v for v in values if v is not None]
    if not clean:
        return None
    return 100.0 * sum(v > 0 for v in clean) / len(clean)


def _public_post(row: dict[str, str]) -> dict[str, Any]:
    return {
        "tweet_id": row.get("tweet_id"),
        "url": row.get("url"),
        "date_utc": row.get("date_utc"),
        "post_type": row.get("post_type"),
        "categories": row.get("categories"),
        "text_summary": row.get("text"),
        "impressions": _int(row.get("impressions")),
        "engagement_count": _int(row.get("engagement_count")),
        "WTI_range_event0_2_lift_pct": _float(row.get("WTI_range_event0_2_lift_pct")),
        "BRENT_range_event0_2_lift_pct": _float(row.get("BRENT_range_event0_2_lift_pct")),
        "WTI_notional_event0_2_lift_pct": _float(row.get("WTI_notional_event0_2_lift_pct")),
        "BRENT_notional_event0_2_lift_pct": _float(row.get("BRENT_notional_event0_2_lift_pct")),
        "WTI_notional_event0_2_per_day": _float(row.get("WTI_notional_event0_2_per_day")),
        "BRENT_notional_event0_2_per_day": _float(row.get("BRENT_notional_event0_2_per_day")),
    }


def _stage_dashboard_downloads(files: list[Path], out_dir: Path) -> list[dict[str, str]]:
    """Copy dashboard-downloadable artifacts under dashboard/data/downloads.

    The dashboard is intentionally static/portable, so links must work when the
    dashboard directory is served as its own site root.
    """
    downloads_dir = out_dir / "downloads"
    downloads_dir.mkdir(parents=True, exist_ok=True)
    staged: list[dict[str, str]] = []
    for source in files:
        target = downloads_dir / source.name
        shutil.copyfile(source, target)
        staged.append({"source": str(source), "href": f"data/downloads/{source.name}"})
    return staged


def _plain_inline_markdown(text: str) -> str:
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    return text.strip()


def _report_sections(report_path: Path, max_sections: int = 8) -> list[dict[str, Any]]:
    """Parse the public Phase 1 report draft into dashboard-friendly sections.

    This intentionally keeps the dashboard static and dependency-free; richer markdown
    rendering can be added in public packaging later without changing the data contract.
    """
    text = report_path.read_text(encoding="utf-8")
    sections: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if line.startswith("## "):
            if current:
                sections.append(current)
            current = {"heading": line[3:].strip(), "paragraphs": [], "bullets": [], "quote": None}
            continue
        if current is None or line.startswith("# ") or line.startswith("**Draft:") or line.startswith("**Date:") or line.startswith("**Scope:") or line.startswith("**Status:"):
            continue
        if not line:
            continue
        if line.startswith("> ") and current.get("quote") is None:
            current["quote"] = _plain_inline_markdown(line[2:])
        elif line.startswith("- ") and len(current["bullets"]) < 8:
            current["bullets"].append(_plain_inline_markdown(line[2:]))
        elif not re.match(r"^\d+\. ", line) and not line.startswith("### ") and len(current["paragraphs"]) < 3:
            current["paragraphs"].append(_plain_inline_markdown(line))

    if current:
        sections.append(current)

    priority = [
        "Executive Summary",
        "Study Design at a Glance",
        "Main Result: WTI Shows a Positive Directional Relationship",
        "Brent Result: Interesting but Underpowered",
        "Social Performance: Reach and Activity Are Different Signals",
        "What This Supports",
        "What This Does Not Prove",
        "Final Conclusion",
    ]
    by_heading = {s["heading"]: s for s in sections}
    selected = [by_heading[h] for h in priority if h in by_heading]
    if len(selected) < max_sections:
        selected.extend(s for s in sections if s["heading"] not in priority)
    return selected[:max_sections]


def _market_control_summary(market_rows: list[dict[str, str]], high_vol_rows: list[dict[str, str]]) -> dict[str, Any]:
    hv_post = [r for r in high_vol_rows if _bool(r.get("has_oil_post"))]
    hv_no_post = [r for r in high_vol_rows if not _bool(r.get("has_oil_post"))]
    all_post = [r for r in market_rows if _bool(r.get("has_oil_post"))]
    all_no_post = [r for r in market_rows if not _bool(r.get("has_oil_post"))]

    def activity(rows: list[dict[str, str]]) -> dict[str, float | int | None]:
        return {
            "day_count": len(rows),
            "median_activity_lift_pct": _median([_float(r.get("activity_event0_2_lift_pct")) for r in rows]),
            "median_event_notional_per_day": _median([_float(r.get("activity_event0_2_notional_per_day")) for r in rows]),
            "positive_activity_lift_pct": _pct_positive([_float(r.get("activity_event0_2_lift_pct")) for r in rows]),
        }

    return {
        "eligible_days": len(market_rows),
        "high_vol_days": len(high_vol_rows),
        "high_vol_post_days": len(hv_post),
        "high_vol_no_post_days": len(hv_no_post),
        "high_vol_post_activity": activity(hv_post),
        "high_vol_no_post_activity": activity(hv_no_post),
        "all_post_activity": activity(all_post),
        "all_no_post_activity": activity(all_no_post),
    }


def _control_day(row: dict[str, str]) -> dict[str, Any]:
    return {
        "date_utc": row.get("date_utc"),
        "market": row.get("market"),
        "range_pct": _float(row.get("range_pct")),
        "range_lift_pct": _float(row.get("range_lift_pct")),
        "range_percentile_vs_baseline": _float(row.get("range_percentile_vs_baseline")),
        "range_baseline_obs": _int(row.get("range_baseline_obs")),
        "has_oil_post": _bool(row.get("has_oil_post")),
        "oil_post_count": _int(row.get("oil_post_count")),
        "oil_original_count": _int(row.get("oil_original_count")),
        "top_oil_post_impressions": _int(row.get("top_oil_post_impressions")),
        "activity_event0_2_notional_per_day": _float(row.get("activity_event0_2_notional_per_day")),
        "activity_event0_2_lift_pct": _float(row.get("activity_event0_2_lift_pct")),
        "activity_event0_2_fills_per_day": _float(row.get("activity_event0_2_fills_per_day")),
        "activity_event0_2_fills_lift_pct": _float(row.get("activity_event0_2_fills_lift_pct")),
        "activity_event0_2_partial": _bool(row.get("activity_event0_2_partial")),
    }


def _event_market_summary(event_rows: list[dict[str, str]], market: str) -> dict[str, Any]:
    range_lifts = [_float(r.get(f"{market}_range_event0_2_lift_pct")) for r in event_rows]
    activity_lifts = [_float(r.get(f"{market}_notional_event0_2_lift_pct")) for r in event_rows]
    activity_48h = [_float(r.get(f"{market}_notional_post_event48h_lift_pct")) for r in event_rows]
    activity_72h = [_float(r.get(f"{market}_notional_post_event72h_lift_pct")) for r in event_rows]
    return {
        "range_positive_pct": _pct_positive(range_lifts),
        "activity_positive_pct": _pct_positive(activity_lifts),
        "activity_48h_positive_pct": _pct_positive(activity_48h),
        "activity_72h_positive_pct": _pct_positive(activity_72h),
        "median_range_lift_pct": _median(range_lifts),
        "median_activity_lift_pct": _median(activity_lifts),
        "positive_counts": {
            "range_0_2d": sum((v or 0) > 0 for v in range_lifts if v is not None),
            "activity_0_2d": sum((v or 0) > 0 for v in activity_lifts if v is not None),
            "activity_48h": sum((v or 0) > 0 for v in activity_48h if v is not None),
            "activity_72h": sum((v or 0) > 0 for v in activity_72h if v is not None),
        },
    }


def build_dashboard_bundle(study_path: Path, out_dir: Path) -> dict[str, Any]:
    study_path = study_path.resolve()
    config = load_simple_yaml(study_path)
    repo_root = repo_root_for(study_path)
    out_dir.mkdir(parents=True, exist_ok=True)

    event_csv = resolve_path(repo_root, get_nested(config, ["paths", "reports", "event_study_csv"]))
    control_csv = resolve_path(repo_root, get_nested(config, ["paths", "reports", "volatility_control_csv"]))
    report_md = repo_root / "reports" / "ostium-social-volatility-public-report-draft.md"
    methodology_md = repo_root / "reports" / "ostium-social-volatility-methodology-appendix.md"
    event_rows = _read_csv(event_csv)
    control_rows = _read_csv(control_csv)

    high_threshold = _float(get_nested(config, ["volatility", "high_volatility_definition", "range_percentile_gte"], 75)) or 75.0
    lift_gt = _float(get_nested(config, ["volatility", "high_volatility_definition", "range_lift_pct_gt"], 0))
    lift_gt = 0.0 if lift_gt is None else lift_gt
    high_vol = [
        r for r in control_rows
        if (_float(r.get("range_lift_pct")) is not None and _float(r.get("range_lift_pct")) > lift_gt)
        and (_float(r.get("range_percentile_vs_baseline")) is not None and _float(r.get("range_percentile_vs_baseline")) >= high_threshold)
    ]

    markets: dict[str, dict[str, Any]] = {}
    for label in sorted({r.get("market", "") for r in control_rows if r.get("market")}):
        market_rows = [r for r in control_rows if r.get("market") == label]
        market_hv = [r for r in high_vol if r.get("market") == label]
        markets[label] = _market_control_summary(market_rows, market_hv)

    top_social = sorted(event_rows, key=lambda r: _int(r.get("impressions")), reverse=True)[:10]
    top_wti_activity = sorted(
        event_rows,
        key=lambda r: _float(r.get("WTI_notional_event0_2_per_day")) or 0,
        reverse=True,
    )[:10]
    download_sources = [event_csv, control_csv, report_md, methodology_md]
    staged_downloads = _stage_dashboard_downloads(download_sources, out_dir)
    href_by_name = {Path(item["source"]).name: item["href"] for item in staged_downloads}

    payload: dict[str, Any] = {
        "phase": "Phase 3 — Dashboard",
        "canonical_phases": [
            "Phase 1 — Research report package",
            "Phase 2 — Reproducible pipeline cleanup",
            "Phase 3 — Dashboard",
            "Phase 4 — Hermes skill / agent runbook",
            "Phase 5 — Public GitHub packaging",
            "Phase 6 — Optional live v2",
        ],
        "source_phase_dependency": "Phase 2 cached pipeline outputs",
        "study": {
            "id": get_nested(config, ["study", "id"]),
            "title": get_nested(config, ["study", "title"]),
            "config": str(study_path.relative_to(repo_root) if study_path.is_relative_to(repo_root) else study_path),
        },
        "report": {
            "title": "Ostium Social Volatility Study: Oil/Hormuz Posting, Market Volatility, and Trading Activity",
            "status": "Phase 1 public-facing draft embedded for Phase 3 dashboard readability; not public-published.",
            "sections": _report_sections(report_md),
        },
        "event_study": {
            "post_count": len(event_rows),
            "unique_dates": len({r.get("date_utc") for r in event_rows}),
            "total_impressions": sum(_int(r.get("impressions")) for r in event_rows),
            "posts": [_public_post(r) for r in event_rows],
            "top_social_posts": [_public_post(r) for r in top_social],
            "top_wti_activity_posts": [_public_post(r) for r in top_wti_activity],
            "market_summaries": {
                "WTI": _event_market_summary(event_rows, "WTI"),
                "BRENT": _event_market_summary(event_rows, "BRENT"),
            },
        },
        "volatility_control": {
            "row_count": len(control_rows),
            "high_vol_rows": len(high_vol),
            "high_vol_definition": {
                "range_lift_pct_gt": lift_gt,
                "range_percentile_gte": high_threshold,
            },
            "markets": markets,
            "days": [_control_day(r) for r in control_rows],
        },
        "assumptions": {
            "primary_event_window": get_nested(config, ["windows", "calendar", "primary_event", "display"]),
            "calendar_baseline_days": get_nested(config, ["windows", "calendar", "baseline_days"]),
            "post_time_robustness": [
                item.get("label") for item in get_nested(config, ["windows", "post_time", "robustness"], [])
            ],
            "activity_source": get_nested(config, ["activity", "source"]),
            "notional_formula": get_nested(config, ["activity", "metrics", "primary_notional_formula"]),
            "default_high_volatility_definition": {
                "range_lift_pct_gt": lift_gt,
                "range_percentile_gte": high_threshold,
            },
        },
        "generated_files": {
            "event_study_csv": str(event_csv.relative_to(repo_root)),
            "volatility_control_csv": str(control_csv.relative_to(repo_root)),
            "report_markdown": str(report_md.relative_to(repo_root)),
            "methodology_markdown": str(methodology_md.relative_to(repo_root)),
        },
        "dashboard_downloads": [
            {"label": "Event-study CSV", "href": href_by_name[event_csv.name]},
            {"label": "Volatility-control CSV", "href": href_by_name[control_csv.name]},
            {"label": "Public report draft", "href": href_by_name[report_md.name]},
            {"label": "Methodology appendix", "href": href_by_name[methodology_md.name]},
        ],
    }
    (out_dir / "summary.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Build the static dashboard data bundle.")
    parser.add_argument("--study", type=Path, default=Path("configs/study.oil-hormuz.example.yaml"))
    parser.add_argument("--out-dir", type=Path, default=Path("dashboard/data"))
    args = parser.parse_args(argv)
    payload = build_dashboard_bundle(args.study, args.out_dir)
    print(json.dumps({"ok": True, "out": str(args.out_dir / "summary.json"), "post_count": payload["event_study"]["post_count"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
