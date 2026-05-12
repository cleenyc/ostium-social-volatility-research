#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path
from statistics import median
from typing import Any

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from ostium_social_volatility.event_study import lift_vs_baseline, per_day_value
from ostium_social_volatility.market import MarketDay, event_study_lift, window_days
from ostium_social_volatility.metrics import engagement_count, impression_count, oil_categories, post_type
from ostium_social_volatility.validate import get_nested, load_simple_yaml

RAW_ACTIVITY = REPO / "data" / "raw" / "event_study_activity_windows" / "event_study_activity_windows_summary.json"
RAW_MARKET_DIR = REPO / "data" / "raw" / "market_ohlc"
PROCESSED = REPO / "data" / "processed"
REPORTS = REPO / "reports"
for d in [RAW_MARKET_DIR, PROCESSED, REPORTS]:
    d.mkdir(parents=True, exist_ok=True)

MARKETS = {
    "WTI": "CL-USD_daily_ohlc.csv",
    "BRENT": "BRENT-USD_daily_ohlc.csv",
}
EVENT_REPORT_MD = REPORTS / "ostium-oil-hormuz-event-study-v1_3.md"
EVENT_REPORT_CSV = REPORTS / "ostium-oil-hormuz-event-study-v1_3.csv"
MARKET_WINDOWS_CSV = PROCESSED / "market_volatility_event_windows.csv"
EVENT_ACTIVITY_CSV = PROCESSED / "event_study_activity_windows.csv"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def parse_date(value: str) -> date:
    return date.fromisoformat(value[:10])


def one_line(text: str, n: int = 170) -> str:
    t = " ".join((text or "").replace("\n", " ").split())
    return t if len(t) <= n else t[: n - 1] + "…"


def money(x: float | int | None) -> str:
    return "n/a" if x is None else f"${x:,.0f}"


def pct(x: float | None) -> str:
    return "n/a" if x is None else f"{x:+.1f}%"


def num(x: float | None, digits: int = 1) -> str:
    return "n/a" if x is None else f"{x:.{digits}f}"


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    fields = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def copy_ohlc_inputs() -> None:
    """Verify cached OHLC fixture files are present.

    Earlier private drafts copied these from a local project-artifacts folder.
    The public package stores the cached OHLC inputs directly under data/raw.
    """
    for filename in MARKETS.values():
        dst = RAW_MARKET_DIR / filename
        if not dst.exists():
            raise FileNotFoundError(dst)


def load_market_days(symbol: str, filename: str) -> dict[date, MarketDay]:
    rows: dict[date, MarketDay] = {}
    with (RAW_MARKET_DIR / filename).open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows[parse_date(r["date"])] = MarketDay(
                date=parse_date(r["date"]),
                symbol=symbol,
                open=float(r["open"]),
                high=float(r["high"]),
                low=float(r["low"]),
                close=float(r["close"]),
            )
    return rows


def select_market_rows(rows_by_date: dict[date, MarketDay], dates: list[date]) -> list[MarketDay]:
    return [rows_by_date[d] for d in dates if d in rows_by_date]


def window_activity(windows: dict[tuple[str, str, str], dict[str, Any]], event_date: str, market: str, segment: str) -> dict[str, Any]:
    return windows[(event_date, market, segment)]


def post_window_activity(windows: dict[tuple[str, str, str], dict[str, Any]], tweet_id: str, market: str, segment: str) -> dict[str, Any]:
    return windows[(tweet_id, market, segment)]


def build_rows(data: dict[str, Any], markets: dict[str, dict[date, MarketDay]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    date_windows = {(w["date"], w["label"], w["segment"]): w for w in data["windows"] if not w.get("postId")}
    post_windows = {(w["postId"], w["label"], w["segment"]): w for w in data["windows"] if w.get("postId")}
    event_rows: list[dict[str, Any]] = []
    market_window_rows: list[dict[str, Any]] = []
    activity_rows: list[dict[str, Any]] = []

    unique_dates = sorted(set(p["date"] for p in data["posts"]))
    for d_str in unique_dates:
        d = parse_date(d_str)
        baseline_dates = window_days(d, -30, -1)
        event_dates = window_days(d, 0, 2)
        context_dates = window_days(d, 0, 7)
        for market, rows_by_date in markets.items():
            baseline_rows = select_market_rows(rows_by_date, baseline_dates)
            event_mkt_rows = select_market_rows(rows_by_date, event_dates)
            context_rows = select_market_rows(rows_by_date, context_dates)
            for metric in ["abs_return_pct", "range_pct"]:
                primary = event_study_lift(event_mkt_rows, baseline_rows, metric=metric)  # type: ignore[arg-type]
                context = event_study_lift(context_rows, baseline_rows, metric=metric)  # type: ignore[arg-type]
                market_window_rows.append({
                    "date_utc": d_str,
                    "market": market,
                    "metric": metric,
                    "baseline30_avg": primary["baseline_avg"],
                    "event0_2_avg": primary["event_avg"],
                    "event0_2_lift_pct": primary["lift_pct"],
                    "event0_2_z_score": primary["z_score"],
                    "event0_2_percentile_vs_baseline": primary["percentile"],
                    "context0_7_avg": context["event_avg"],
                    "context0_7_lift_pct": context["lift_pct"],
                    "baseline_observations": primary["baseline_observations"],
                    "event_observations": primary["event_observations"],
                    "context_observations": context["event_observations"],
                })
            for segment in ["baseline30", "event0_2", "event1_2", "context0_7"]:
                aw = window_activity(date_windows, d_str, market, segment)
                activity_rows.append({
                    "date_utc": d_str,
                    "tweet_id": aw.get("postId"),
                    "market": market,
                    "segment": segment,
                    "start": aw["start"],
                    "end": aw["end"],
                    "days": aw["days"],
                    "is_partial": aw["isPartial"],
                    "fill_count": aw["fillCount"],
                    "fills_per_day": per_day_value(aw, "fillCount"),
                    "notional_usd": aw["notionalUsd"],
                    "notional_usd_per_day": per_day_value(aw, "notionalUsd"),
                    "opening_fees_usd": aw["openingFeesUsd"],
                    "opening_fees_usd_per_day": per_day_value(aw, "openingFeesUsd"),
                    "total_fees_usd": aw["totalFeesUsd"],
                })

    market_lookup = {(r["date_utc"], r["market"], r["metric"]): r for r in market_window_rows}
    activity_lookup = {(r["date_utc"], r["market"], r["segment"]): r for r in activity_rows if not r.get("tweet_id")}

    for p in data["posts"]:
        for market in ["WTI", "BRENT"]:
            for segment in ["post_baseline30", "post_event48h", "post_event72h"]:
                aw = post_window_activity(post_windows, p["id"], market, segment)
                activity_rows.append({
                    "date_utc": p["date"],
                    "tweet_id": p["id"],
                    "market": market,
                    "segment": segment,
                    "start": aw["start"],
                    "end": aw["end"],
                    "days": aw["days"],
                    "is_partial": aw["isPartial"],
                    "fill_count": aw["fillCount"],
                    "fills_per_day": per_day_value(aw, "fillCount"),
                    "notional_usd": aw["notionalUsd"],
                    "notional_usd_per_day": per_day_value(aw, "notionalUsd"),
                    "opening_fees_usd": aw["openingFeesUsd"],
                    "opening_fees_usd_per_day": per_day_value(aw, "openingFeesUsd"),
                    "total_fees_usd": aw["totalFeesUsd"],
                })

    post_activity_lookup = {(r["tweet_id"], r["market"], r["segment"]): r for r in activity_rows if r.get("tweet_id")}

    for p in sorted(data["posts"], key=lambda r: r["created_at"]):
        metrics = p.get("public_metrics") or {}
        row: dict[str, Any] = {
            "tweet_id": p["id"],
            "url": f"https://x.com/ostium/status/{p['id']}",
            "created_at": p["created_at"],
            "date_utc": p["date"],
            "post_type": post_type(p),
            "categories": ";".join(oil_categories(p.get("text", ""))),
            "text": one_line(p.get("text", ""), 240),
            "impressions": impression_count(metrics),
            "engagement_count": engagement_count(metrics),
        }
        for market in ["WTI", "BRENT"]:
            for metric_name, prefix in [("range_pct", "range"), ("abs_return_pct", "abs_return")]:
                mr = market_lookup[(p["date"], market, metric_name)]
                row.update({
                    f"{market}_{prefix}_baseline30_avg_pct": mr["baseline30_avg"],
                    f"{market}_{prefix}_event0_2_avg_pct": mr["event0_2_avg"],
                    f"{market}_{prefix}_event0_2_lift_pct": mr["event0_2_lift_pct"],
                    f"{market}_{prefix}_event0_2_z_score": mr["event0_2_z_score"],
                    f"{market}_{prefix}_event0_2_percentile": mr["event0_2_percentile_vs_baseline"],
                    f"{market}_{prefix}_context0_7_avg_pct": mr["context0_7_avg"],
                    f"{market}_{prefix}_context0_7_lift_pct": mr["context0_7_lift_pct"],
                    f"{market}_{prefix}_baseline_obs": mr["baseline_observations"],
                    f"{market}_{prefix}_event_obs": mr["event_observations"],
                })
            base = activity_lookup[(p["date"], market, "baseline30")]
            ev = activity_lookup[(p["date"], market, "event0_2")]
            ev12 = activity_lookup[(p["date"], market, "event1_2")]
            ctx = activity_lookup[(p["date"], market, "context0_7")]
            post_base = post_activity_lookup[(p["id"], market, "post_baseline30")]
            post48 = post_activity_lookup[(p["id"], market, "post_event48h")]
            post72 = post_activity_lookup[(p["id"], market, "post_event72h")]
            row.update({
                f"{market}_notional_baseline30_per_day": base["notional_usd_per_day"],
                f"{market}_notional_event0_2_per_day": ev["notional_usd_per_day"],
                f"{market}_notional_event0_2_lift_pct": lift_vs_baseline(ev["notional_usd_per_day"], base["notional_usd_per_day"]),
                f"{market}_notional_event1_2_per_day": ev12["notional_usd_per_day"],
                f"{market}_notional_event1_2_lift_pct": lift_vs_baseline(ev12["notional_usd_per_day"], base["notional_usd_per_day"]),
                f"{market}_notional_context0_7_per_day": ctx["notional_usd_per_day"],
                f"{market}_notional_context0_7_lift_pct": lift_vs_baseline(ctx["notional_usd_per_day"], base["notional_usd_per_day"]),
                f"{market}_notional_post_baseline30_per_day": post_base["notional_usd_per_day"],
                f"{market}_notional_post_event48h_per_day": post48["notional_usd_per_day"],
                f"{market}_notional_post_event48h_lift_pct": lift_vs_baseline(post48["notional_usd_per_day"], post_base["notional_usd_per_day"]),
                f"{market}_notional_post_event72h_per_day": post72["notional_usd_per_day"],
                f"{market}_notional_post_event72h_lift_pct": lift_vs_baseline(post72["notional_usd_per_day"], post_base["notional_usd_per_day"]),
                f"{market}_fills_baseline30_per_day": base["fills_per_day"],
                f"{market}_fills_event0_2_per_day": ev["fills_per_day"],
                f"{market}_fills_event0_2_lift_pct": lift_vs_baseline(ev["fills_per_day"], base["fills_per_day"]),
                f"{market}_fills_event1_2_per_day": ev12["fills_per_day"],
                f"{market}_fills_event1_2_lift_pct": lift_vs_baseline(ev12["fills_per_day"], base["fills_per_day"]),
                f"{market}_fills_post_event48h_per_day": post48["fills_per_day"],
                f"{market}_fills_post_event48h_lift_pct": lift_vs_baseline(post48["fills_per_day"], post_base["fills_per_day"]),
                f"{market}_fills_post_event72h_per_day": post72["fills_per_day"],
                f"{market}_fills_post_event72h_lift_pct": lift_vs_baseline(post72["fills_per_day"], post_base["fills_per_day"]),
                f"{market}_opening_fees_event0_2_per_day": ev["opening_fees_usd_per_day"],
                f"{market}_context0_7_partial": ctx["is_partial"],
            })
        event_rows.append(row)
    return event_rows, market_window_rows, activity_rows


def safe_median(vals: list[float]) -> float | None:
    vals = [v for v in vals if v is not None]
    return float(median(vals)) if vals else None


def top_non_null(rows: list[dict[str, Any]], key: str, n: int = 6) -> list[dict[str, Any]]:
    return sorted([r for r in rows if r.get(key) is not None], key=lambda r: r[key], reverse=True)[:n]


def build_report(rows: list[dict[str, Any]], data: dict[str, Any]) -> str:
    impressions_med = safe_median([r["impressions"] for r in rows])
    type_counts = Counter(r["post_type"] for r in rows)
    cat_counts = Counter(c for r in rows for c in r["categories"].split(";") if c)
    partial_context = sum(1 for r in rows if r["WTI_context0_7_partial"] or r["BRENT_context0_7_partial"])

    def capped(v: float | None, low: float = -100.0, high: float = 500.0) -> float:
        if v is None:
            return low
        return min(max(v, low), high)

    def overlap_score(r: dict[str, Any]) -> float:
        social = 1 if impressions_med and r["impressions"] >= impressions_med else 0
        market = max(capped(v) for v in [r["WTI_range_event0_2_lift_pct"], r["BRENT_range_event0_2_lift_pct"]])
        activity = max(capped(v) for v in [
            r["WTI_notional_event0_2_lift_pct"],
            r["BRENT_notional_event0_2_lift_pct"],
            r["WTI_notional_post_event48h_lift_pct"],
            r["BRENT_notional_post_event48h_lift_pct"],
        ])
        return social * 1000 + market + activity

    def activity_signal(r: dict[str, Any]) -> float:
        # Rank by economically meaningful notional/day, not raw pct lift,
        # because Brent launch/ramp baselines can be near-zero and create huge pct values.
        # Exact post-time 48h is preferred; calendar 0–2d remains the continuity window.
        candidates = []
        for market in ["WTI", "BRENT"]:
            lift = r[f"{market}_notional_post_event48h_lift_pct"]
            event = r[f"{market}_notional_post_event48h_per_day"] or 0
            if lift is None or lift > 0:
                candidates.append(event)
            lift = r[f"{market}_notional_event0_2_lift_pct"]
            event = r[f"{market}_notional_event0_2_per_day"] or 0
            if lift is None or lift > 0:
                candidates.append(event)
        return max(candidates or [0])

    top_overlap = sorted(rows, key=overlap_score, reverse=True)[:8]
    top_market = top_non_null(rows, "WTI_range_event0_2_lift_pct", 5) + top_non_null(rows, "BRENT_range_event0_2_lift_pct", 5)
    top_market = sorted({r["tweet_id"]: r for r in top_market}.values(), key=lambda r: max(r["WTI_range_event0_2_lift_pct"] or -999, r["BRENT_range_event0_2_lift_pct"] or -999), reverse=True)[:8]
    top_activity = sorted(rows, key=activity_signal, reverse=True)[:8]
    top_social_only = sorted(rows, key=lambda r: r["impressions"], reverse=True)[:8]

    lines: list[str] = []
    lines.append("# Ostium Oil/Hormuz V1.3 Event-Study Report")
    lines.append("")
    lines.append("Date: 2026-05-12")
    lines.append("")
    lines.append("## Method")
    lines.append("")
    lines.append("- Event unit: each `@Ostium` oil/Hormuz-related post from the 90-day full-archive query.")
    lines.append("- Calendar baseline: 30 calendar days before the event date, end-exclusive.")
    lines.append("- Primary event window remains event date through two days after (`0–2d`, 3 calendar days total).")
    lines.append("- Post-time activity windows: exact tweet timestamp through +48h and +72h, compared with the exact 30 days before tweet timestamp.")
    lines.append("- Robustness activity window: calendar `1–2d`, used as an extra layer rather than the primary framing.")
    lines.append("- Secondary context window: event date through seven days after (`0–7d`), not the headline window.")
    lines.append("- Outcomes: X social metrics, WTI/Brent market volatility, and Ostium SDK WTI/Brent trading activity.")
    lines.append("- Market volatility metrics: intraday range % and absolute open-to-close return %, each compared with the 30-day baseline.")
    lines.append("- Activity metrics: SDK fill notional/day and fills/day compared with the 30-day baseline.")
    lines.append("- Activity rankings use notional/day as the primary economic signal because new Brent launch/ramp periods can have near-zero baselines and extreme percentage lifts.")
    lines.append("")
    lines.append("## Coverage")
    lines.append("")
    lines.append(f"- Posts: {len(rows)} across {len(set(r['date_utc'] for r in rows))} unique event dates.")
    lines.append(f"- Post types: {dict(type_counts)}.")
    lines.append(f"- Oil categories: {dict(cat_counts)}.")
    lines.append(f"- Activity windows collected: {len(data['windows'])}; includes calendar windows and per-post exact post-time windows; WTI pairId 7, Brent pairId 55.")
    lines.append(f"- Partial 0–7d context windows: {partial_context}; primary 0–2d remains the continuity window.")
    lines.append("")
    lines.append("## Strongest combined cases")
    for r in top_overlap:
        lines.append(f"- {r['date_utc']} [{r['post_type']}] impressions {r['impressions']:,}; WTI range lift {pct(r['WTI_range_event0_2_lift_pct'])}; Brent range lift {pct(r['BRENT_range_event0_2_lift_pct'])}; WTI activity 0–2d {pct(r['WTI_notional_event0_2_lift_pct'])}, post+48h {pct(r['WTI_notional_post_event48h_lift_pct'])}; Brent activity 0–2d {pct(r['BRENT_notional_event0_2_lift_pct'])}, post+48h {pct(r['BRENT_notional_post_event48h_lift_pct'])}; {r['url']} — {r['text']}")
    lines.append("")
    lines.append("## Highest market-volatility alignment")
    for r in top_market:
        lines.append(f"- {r['date_utc']} impressions {r['impressions']:,}; WTI 0–2d range {num(r['WTI_range_event0_2_avg_pct'])}% vs baseline {num(r['WTI_range_baseline30_avg_pct'])}% ({pct(r['WTI_range_event0_2_lift_pct'])}); Brent 0–2d range {num(r['BRENT_range_event0_2_avg_pct'])}% vs baseline {num(r['BRENT_range_baseline30_avg_pct'])}% ({pct(r['BRENT_range_event0_2_lift_pct'])}); {r['url']} — {r['text']}")
    lines.append("")
    lines.append("## Highest Ostium WTI/Brent activity signals")
    for r in top_activity:
        lines.append(f"- {r['date_utc']} impressions {r['impressions']:,}; WTI 0–2d {money(r['WTI_notional_event0_2_per_day'])} ({pct(r['WTI_notional_event0_2_lift_pct'])}), post+48h {money(r['WTI_notional_post_event48h_per_day'])} ({pct(r['WTI_notional_post_event48h_lift_pct'])}); Brent 0–2d {money(r['BRENT_notional_event0_2_per_day'])} ({pct(r['BRENT_notional_event0_2_lift_pct'])}), post+48h {money(r['BRENT_notional_post_event48h_per_day'])} ({pct(r['BRENT_notional_post_event48h_lift_pct'])}); {r['url']} — {r['text']}")
    lines.append("")
    lines.append("## Post-time robustness read")
    for r in top_non_null(rows, "WTI_notional_post_event48h_lift_pct", 8):
        lines.append(f"- {r['date_utc']} impressions {r['impressions']:,}; WTI 0–2d {pct(r['WTI_notional_event0_2_lift_pct'])}; WTI 1–2d {pct(r['WTI_notional_event1_2_lift_pct'])}; WTI exact post+48h {pct(r['WTI_notional_post_event48h_lift_pct'])}; WTI exact post+72h {pct(r['WTI_notional_post_event72h_lift_pct'])}; {r['url']} — {r['text']}")
    lines.append("")
    lines.append("## Highest social reach")
    for r in top_social_only:
        lines.append(f"- {r['date_utc']} impressions {r['impressions']:,}; WTI range lift {pct(r['WTI_range_event0_2_lift_pct'])}; WTI activity lift {pct(r['WTI_notional_event0_2_lift_pct'])}; {r['url']} — {r['text']}")
    lines.append("")
    lines.append("## Readout")
    lines.append("")
    lines.append("- v1.3 keeps the v1.2 calendar 0–2d primary window for continuity.")
    lines.append("- Exact post-time activity windows test whether Ostium fills remained elevated after each social post went live.")
    lines.append("- Calendar 1–2d is retained as an extra robustness layer, not as the main replacement window.")
    lines.append("- 0–7d is retained only as context, because it can pick up unrelated market/protocol movements.")
    lines.append("- This remains correlational: without competitor per-market volumes or randomized exposure, it cannot prove causality.")
    lines.append("")
    lines.append("## Generated files")
    lines.append("")
    lines.append(f"- `{rel(EVENT_REPORT_MD)}`")
    lines.append(f"- `{rel(EVENT_REPORT_CSV)}`")
    lines.append(f"- `{rel(MARKET_WINDOWS_CSV)}`")
    lines.append(f"- `{rel(EVENT_ACTIVITY_CSV)}`")
    return "\n".join(lines) + "\n"


def rel(path: Path) -> str:
    try:
        return path.relative_to(REPO).as_posix()
    except ValueError:
        return path.as_posix()


def resolve_repo_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else REPO / path


def configure_from_study(study_path: Path) -> None:
    global RAW_ACTIVITY, RAW_MARKET_DIR, PROCESSED, REPORTS, MARKETS
    global EVENT_REPORT_MD, EVENT_REPORT_CSV, MARKET_WINDOWS_CSV, EVENT_ACTIVITY_CSV

    config = load_simple_yaml(study_path)
    RAW_ACTIVITY = resolve_repo_path(get_nested(config, ["paths", "raw", "event_study_activity_windows"]))
    RAW_MARKET_DIR = resolve_repo_path(get_nested(config, ["paths", "raw", "market_ohlc_dir"]))
    EVENT_REPORT_MD = resolve_repo_path(get_nested(config, ["paths", "reports", "event_study_md"]))
    EVENT_REPORT_CSV = resolve_repo_path(get_nested(config, ["paths", "reports", "event_study_csv"]))
    MARKET_WINDOWS_CSV = resolve_repo_path(get_nested(config, ["paths", "processed", "market_volatility_event_windows"]))
    EVENT_ACTIVITY_CSV = resolve_repo_path(get_nested(config, ["paths", "processed", "event_study_activity_windows"]))
    PROCESSED = EVENT_ACTIVITY_CSV.parent
    REPORTS = EVENT_REPORT_CSV.parent
    MARKETS = {
        str(market["label"]): f"{market['ostium_builder_symbol']}_daily_ohlc.csv"
        for market in get_nested(config, ["markets"], [])
    }
    for path in [RAW_MARKET_DIR, PROCESSED, REPORTS, EVENT_REPORT_MD.parent, EVENT_REPORT_CSV.parent, MARKET_WINDOWS_CSV.parent, EVENT_ACTIVITY_CSV.parent]:
        path.mkdir(parents=True, exist_ok=True)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate the v1.3 event-study report.")
    parser.add_argument(
        "--study",
        type=Path,
        default=REPO / "configs" / "study.oil-hormuz.example.yaml",
        help="Study YAML config; defaults to the oil/Hormuz example config.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    configure_from_study(args.study)
    copy_ohlc_inputs()
    data = load_json(RAW_ACTIVITY)
    if data.get("errors"):
        raise RuntimeError(f"Activity collection has errors: {data['errors'][:3]}")
    markets = {market: load_market_days(market, filename) for market, filename in MARKETS.items()}
    rows, market_rows, activity_rows = build_rows(data, markets)
    write_csv(EVENT_REPORT_CSV, rows)
    write_csv(MARKET_WINDOWS_CSV, market_rows)
    write_csv(EVENT_ACTIVITY_CSV, activity_rows)
    report = build_report(rows, data)
    EVENT_REPORT_MD.write_text(report)
    print(json.dumps({
        "report": rel(EVENT_REPORT_MD),
        "event_table": rel(EVENT_REPORT_CSV),
        "posts": len(rows),
        "unique_dates": len(set(r["date_utc"] for r in rows)),
        "market_windows": len(market_rows),
        "activity_windows": len(activity_rows),
    }, indent=2))


if __name__ == "__main__":
    main()
