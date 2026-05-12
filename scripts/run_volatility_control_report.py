#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
import sys
from collections import Counter
from datetime import date, timedelta
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from ostium_social_volatility.event_study import lift_vs_baseline, per_day_value
from ostium_social_volatility.market import MarketDay, event_study_lift, window_days
from ostium_social_volatility.validate import get_nested, load_simple_yaml

RAW_CONTROL = REPO / "data" / "raw" / "volatility_control_activity_windows" / "volatility_control_activity_windows_summary.json"
RAW_MARKET_DIR = REPO / "data" / "raw" / "market_ohlc"
PROCESSED = REPO / "data" / "processed"
REPORTS = REPO / "reports"
EVENT_TABLE = REPORTS / "ostium-oil-hormuz-event-study-v1_3.csv"

MARKETS = {
    "WTI": "CL-USD_daily_ohlc.csv",
    "BRENT": "BRENT-USD_daily_ohlc.csv",
}
HIGH_VOL_PERCENTILE = 75.0
MIN_BASELINE_OBS = 10
CONTROL_REPORT_MD = REPORTS / "ostium-oil-hormuz-volatility-control-v1_4.md"
CONTROL_REPORT_CSV = REPORTS / "ostium-oil-hormuz-volatility-control-v1_4.csv"
PROCESSED_CONTROL_CSV = PROCESSED / "volatility_control_days.csv"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def parse_date(value: str) -> date:
    return date.fromisoformat(value[:10])


def money(x: float | int | None) -> str:
    return "n/a" if x is None else f"${x:,.0f}"


def pct(x: float | None) -> str:
    return "n/a" if x is None else f"{x:+.1f}%"


def num(x: float | None, digits: int = 1) -> str:
    return "n/a" if x is None else f"{x:.{digits}f}"


def mean(vals: list[float]) -> float | None:
    return sum(vals) / len(vals) if vals else None


def median(vals: list[float]) -> float | None:
    return statistics.median(vals) if vals else None


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    fields = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


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


def load_oil_post_dates() -> dict[str, Any]:
    by_date: dict[str, list[dict[str, Any]]] = {}
    with EVENT_TABLE.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            by_date.setdefault(r["date_utc"], []).append(r)
    return {
        "by_date": by_date,
        "dates": set(by_date),
        "post_count": sum(len(v) for v in by_date.values()),
    }


def control_window_lookup(data: dict[str, Any]) -> dict[tuple[str, str, str], dict[str, Any]]:
    return {(w["date"], w["label"], w["segment"]): w for w in data["windows"]}


def build_rows(data: dict[str, Any], markets: dict[str, dict[date, MarketDay]], posts: dict[str, Any]) -> list[dict[str, Any]]:
    windows = control_window_lookup(data)
    rows: list[dict[str, Any]] = []
    for market, rows_by_date in markets.items():
        for d in sorted(rows_by_date):
            baseline_dates = window_days(d, -30, -1)
            baseline_rows = [rows_by_date[x] for x in baseline_dates if x in rows_by_date]
            primary = event_study_lift([rows_by_date[d]], baseline_rows, metric="range_pct")
            if primary["baseline_observations"] < MIN_BASELINE_OBS:
                continue
            base = windows[(d.isoformat(), market, "baseline30")]
            ev = windows[(d.isoformat(), market, "event0_2")]
            base_notional = per_day_value(base, "notionalUsd")
            ev_notional = per_day_value(ev, "notionalUsd")
            date_posts = posts["by_date"].get(d.isoformat(), [])
            rows.append({
                "date_utc": d.isoformat(),
                "market": market,
                "range_pct": rows_by_date[d].range_pct,
                "range_baseline30_avg_pct": primary["baseline_avg"],
                "range_lift_pct": primary["lift_pct"],
                "range_percentile_vs_baseline": primary["percentile"],
                "range_baseline_obs": primary["baseline_observations"],
                "has_oil_post": bool(date_posts),
                "oil_post_count": len(date_posts),
                "oil_original_count": sum(1 for p in date_posts if p["post_type"] == "original"),
                "top_oil_post_impressions": max([int(float(p["impressions"] or 0)) for p in date_posts] or [0]),
                "activity_baseline30_notional_per_day": base_notional,
                "activity_event0_2_notional_per_day": ev_notional,
                "activity_event0_2_lift_pct": lift_vs_baseline(ev_notional, base_notional),
                "activity_baseline30_fills_per_day": per_day_value(base, "fillCount"),
                "activity_event0_2_fills_per_day": per_day_value(ev, "fillCount"),
                "activity_event0_2_fills_lift_pct": lift_vs_baseline(per_day_value(ev, "fillCount"), per_day_value(base, "fillCount")),
                "activity_event0_2_partial": ev["isPartial"],
            })
    return rows


def high_vol_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        r for r in rows
        if r["range_lift_pct"] is not None
        and r["range_lift_pct"] > 0
        and r["range_percentile_vs_baseline"] is not None
        and r["range_percentile_vs_baseline"] >= HIGH_VOL_PERCENTILE
    ]


def group_stats(rows: list[dict[str, Any]]) -> dict[str, Any]:
    lifts = [r["activity_event0_2_lift_pct"] for r in rows if r["activity_event0_2_lift_pct"] is not None]
    notionals = [r["activity_event0_2_notional_per_day"] for r in rows if r["activity_event0_2_notional_per_day"] is not None]
    return {
        "days": len(rows),
        "median_activity_lift_pct": median(lifts),
        "mean_activity_lift_pct": mean(lifts),
        "positive_activity_lift_days": sum(1 for v in lifts if v > 0),
        "median_event_notional_per_day": median(notionals),
        "mean_event_notional_per_day": mean(notionals),
    }


def corr(rows: list[dict[str, Any]], x: str, y: str) -> tuple[float | None, int]:
    pairs = [(r[x], r[y]) for r in rows if r.get(x) is not None and r.get(y) is not None]
    if len(pairs) < 2:
        return None, len(pairs)
    xs = [a for a, _ in pairs]
    ys = [b for _, b in pairs]
    mx = mean(xs) or 0
    my = mean(ys) or 0
    numr = sum((a - mx) * (b - my) for a, b in pairs)
    den = math.sqrt(sum((a - mx) ** 2 for a in xs) * sum((b - my) ** 2 for b in ys))
    return (numr / den if den else None), len(pairs)


def build_report(rows: list[dict[str, Any]], data: dict[str, Any], posts: dict[str, Any]) -> str:
    hv = high_vol_rows(rows)
    by_market = {m: [r for r in rows if r["market"] == m] for m in MARKETS}
    hv_by_market = {m: [r for r in hv if r["market"] == m] for m in MARKETS}
    lines: list[str] = []
    lines.append("# Ostium Oil/Hormuz V1.4 Volatility-Day Control Report")
    lines.append("")
    lines.append("Date: 2026-05-12")
    lines.append("")
    lines.append("## Method")
    lines.append("")
    lines.append("- Question: on high oil-volatility days, was Ostium activity higher when Ostium posted oil content than when it did not?")
    lines.append("- Markets: WTI over all available WTI OHLC days; Brent over all available Brent OHLC days.")
    lines.append("- Eligible market days require at least 10 prior OHLC observations in the 30-day rolling baseline.")
    lines.append(f"- High-volatility definition: daily range lift > 0 and daily range percentile vs rolling baseline >= {HIGH_VOL_PERCENTILE:.0f}th percentile.")
    lines.append("- Post flag: date has at least one oil/Hormuz-related `@Ostium` post from the v1.3 event table.")
    lines.append("- Activity outcome: Ostium SDK notional/day in the calendar `0–2d` window vs the prior 30-day activity baseline.")
    lines.append("- This is a control comparison, not causal proof; oil posts are not randomized and may be triggered by the same volatility that drives trading.")
    lines.append("")
    lines.append("## Coverage")
    lines.append("")
    lines.append(f"- Oil posts available: {posts['post_count']} posts across {len(posts['dates'])} dates.")
    lines.append(f"- Raw activity windows collected: {len(data['windows'])}.")
    for market, market_rows in by_market.items():
        dates = [r["date_utc"] for r in market_rows]
        lines.append(f"- {market}: {len(market_rows)} eligible market days ({min(dates)} to {max(dates)}); high-volatility days: {len(hv_by_market[market])}.")
    lines.append("")
    lines.append("## High-volatility post vs no-post comparison")
    lines.append("")
    for market in MARKETS:
        post_days = [r for r in hv_by_market[market] if r["has_oil_post"]]
        no_post_days = [r for r in hv_by_market[market] if not r["has_oil_post"]]
        ps = group_stats(post_days)
        ns = group_stats(no_post_days)
        lines.append(f"### {market}")
        lines.append("")
        lines.append(f"- High-volatility days with oil post: {ps['days']}; without oil post: {ns['days']}.")
        lines.append(f"- Median activity lift with oil post: {pct(ps['median_activity_lift_pct'])}; without oil post: {pct(ns['median_activity_lift_pct'])}.")
        lines.append(f"- Mean activity lift with oil post: {pct(ps['mean_activity_lift_pct'])}; without oil post: {pct(ns['mean_activity_lift_pct'])}.")
        lines.append(f"- Positive activity-lift days with oil post: {ps['positive_activity_lift_days']}/{ps['days']}; without oil post: {ns['positive_activity_lift_days']}/{ns['days']}.")
        lines.append(f"- Median event notional/day with oil post: {money(ps['median_event_notional_per_day'])}; without oil post: {money(ns['median_event_notional_per_day'])}.")
        lines.append("")
    lines.append("## Highest-volatility days")
    lines.append("")
    for market in MARKETS:
        lines.append(f"### {market}")
        for r in sorted(hv_by_market[market], key=lambda x: x["range_lift_pct"] or -999, reverse=True)[:10]:
            flag = "post" if r["has_oil_post"] else "no post"
            lines.append(f"- {r['date_utc']} [{flag}]; range {num(r['range_pct'])}% vs baseline {num(r['range_baseline30_avg_pct'])}% ({pct(r['range_lift_pct'])}); activity lift {pct(r['activity_event0_2_lift_pct'])}; notional/day {money(r['activity_event0_2_notional_per_day'])}; oil posts {r['oil_post_count']}.")
        lines.append("")
    lines.append("## Correlation checks")
    lines.append("")
    for market in MARKETS:
        c_all, n_all = corr(by_market[market], "range_lift_pct", "activity_event0_2_lift_pct")
        c_hv, n_hv = corr(hv_by_market[market], "range_lift_pct", "activity_event0_2_lift_pct")
        lines.append(f"- {market}: range-lift vs activity-lift correlation across eligible days: {num(c_all, 2)} (n={n_all}); across high-volatility days: {num(c_hv, 2)} (n={n_hv}).")
    lines.append("")
    lines.append("## Readout")
    lines.append("")
    lines.append("- V1.4 adds the missing control group: high-volatility days with no oil post.")
    lines.append("- Interpret median/positive-day differences as directional evidence only, because post timing is endogenous to market volatility and campaign decisions.")
    lines.append("- If high-volatility post days show materially higher activity than no-post days, that supports the thesis that posting may amplify activity beyond volatility alone.")
    lines.append("")
    lines.append("## Generated files")
    lines.append("")
    lines.append(f"- `{rel(CONTROL_REPORT_MD)}`")
    lines.append(f"- `{rel(CONTROL_REPORT_CSV)}`")
    lines.append(f"- `{rel(PROCESSED_CONTROL_CSV)}`")
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
    global RAW_CONTROL, RAW_MARKET_DIR, PROCESSED, REPORTS, EVENT_TABLE
    global MARKETS, HIGH_VOL_PERCENTILE, MIN_BASELINE_OBS
    global CONTROL_REPORT_MD, CONTROL_REPORT_CSV, PROCESSED_CONTROL_CSV

    config = load_simple_yaml(study_path)
    RAW_CONTROL = resolve_repo_path(get_nested(config, ["paths", "raw", "volatility_control_activity_windows"]))
    RAW_MARKET_DIR = resolve_repo_path(get_nested(config, ["paths", "raw", "market_ohlc_dir"]))
    EVENT_TABLE = resolve_repo_path(get_nested(config, ["paths", "reports", "event_study_csv"]))
    CONTROL_REPORT_MD = resolve_repo_path(get_nested(config, ["paths", "reports", "volatility_control_md"]))
    CONTROL_REPORT_CSV = resolve_repo_path(get_nested(config, ["paths", "reports", "volatility_control_csv"]))
    PROCESSED_CONTROL_CSV = resolve_repo_path(get_nested(config, ["paths", "processed", "volatility_control_days"]))
    PROCESSED = PROCESSED_CONTROL_CSV.parent
    REPORTS = CONTROL_REPORT_CSV.parent
    MARKETS = {
        str(market["label"]): f"{market['ostium_builder_symbol']}_daily_ohlc.csv"
        for market in get_nested(config, ["markets"], [])
    }
    HIGH_VOL_PERCENTILE = float(get_nested(config, ["volatility", "high_volatility_definition", "range_percentile_gte"], 75.0))
    MIN_BASELINE_OBS = int(get_nested(config, ["volatility", "min_baseline_observations"], 10))
    for path in [PROCESSED_CONTROL_CSV.parent, CONTROL_REPORT_CSV.parent, CONTROL_REPORT_MD.parent]:
        path.mkdir(parents=True, exist_ok=True)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate the v1.4 volatility-control report.")
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
    data = load_json(RAW_CONTROL)
    if data.get("errors"):
        raise RuntimeError(f"Activity collection has errors: {data['errors'][:3]}")
    markets = {market: load_market_days(market, filename) for market, filename in MARKETS.items()}
    posts = load_oil_post_dates()
    rows = build_rows(data, markets, posts)
    write_csv(PROCESSED_CONTROL_CSV, rows)
    write_csv(CONTROL_REPORT_CSV, rows)
    report = build_report(rows, data, posts)
    CONTROL_REPORT_MD.write_text(report)
    print(json.dumps({
        "report": rel(CONTROL_REPORT_MD),
        "table": rel(CONTROL_REPORT_CSV),
        "rows": len(rows),
        "high_vol_rows": len(high_vol_rows(rows)),
        "markets": dict(Counter(r["market"] for r in rows)),
    }, indent=2))


if __name__ == "__main__":
    main()
