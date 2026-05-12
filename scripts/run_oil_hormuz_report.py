#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from ostium_social_volatility.metrics import (
    dt_from_x,
    engagement_count,
    impression_count,
    is_oil_text,
    pct_change,
    safe_median,
)

REPO = Path(__file__).resolve().parents[1]
RAW = REPO / "data" / "raw"
LEGACY_BASELINE = RAW / "legacy_social_baselines"
PROCESSED = REPO / "data" / "processed"
REPORTS = REPO / "reports"
PROCESSED.mkdir(parents=True, exist_ok=True)
REPORTS.mkdir(parents=True, exist_ok=True)

EVENTS = {
    "apr13_canonical": {
        "title": "Apr 13 canonical Hormuz/oil-shock post",
        "tweet_id": "2043652069979275728",
        "event_dates": ["2026-04-13"],
    },
    "mar9_10_cluster": {
        "title": "Mar 9–10 oil/Hormuz cluster",
        "tweet_id": None,
        "event_dates": ["2026-03-09", "2026-03-10"],
    },
}


def rel(path: Path) -> str:
    try:
        return path.relative_to(REPO).as_posix()
    except ValueError:
        return path.as_posix()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def money(x: float | int | None) -> str:
    if x is None:
        return "n/a"
    return f"${x:,.0f}"


def pct(x: float | None) -> str:
    if x is None:
        return "n/a"
    return f"{x:+.1f}%"


def one_line(text: str, n: int = 150) -> str:
    t = " ".join((text or "").replace("\n", " ").split())
    return t if len(t) <= n else t[: n - 1] + "…"


def post_row(p: dict[str, Any]) -> dict[str, Any]:
    m = p.get("public_metrics", {})
    dt = dt_from_x(p["created_at"])
    imp = impression_count(m)
    eng = engagement_count(m)
    return {
        "tweet_id": p["id"],
        "url": f"https://x.com/ostium/status/{p['id']}",
        "created_at": p["created_at"],
        "date_utc": dt.date().isoformat(),
        "text": one_line(p.get("text", ""), 240),
        "is_oil": is_oil_text(p.get("text", "")),
        "impressions": imp,
        "engagement_count": eng,
        "engagement_rate_pct": (eng / imp * 100) if imp else None,
        "retweets": int(m.get("retweet_count") or 0),
        "replies": int(m.get("reply_count") or 0),
        "likes": int(m.get("like_count") or 0),
        "quotes": int(m.get("quote_count") or 0),
        "bookmarks": int(m.get("bookmark_count") or 0),
    }


def read_posts(path: Path) -> list[dict[str, Any]]:
    data = load_json(path)
    return [post_row(p) for p in data.get("data", [])]


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    fields = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def load_activity_windows() -> list[dict[str, Any]]:
    summary = load_json(RAW / "activity_windows" / "activity_windows_summary.json")
    return summary["windows"]


def normalize_activity_windows(windows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for w in windows:
        rows.append(
            {
                "event": w["event"],
                "segment": w["segment"],
                "market": w["label"],
                "pair_id": w["pairId"],
                "symbol": w["symbol"],
                "start": w["start"],
                "end": w["end"],
                "fill_count": w["fillCount"],
                "notional_usd": w["notionalUsd"],
                "opening_fees_usd": w["openingFeesUsd"],
                "total_fees_usd": w["totalFeesUsd"],
                "actions_json": json.dumps(w.get("actions", {}), sort_keys=True),
                "sides_json": json.dumps(w.get("sides", {}), sort_keys=True),
            }
        )
    return rows


def activity_by_event_market(rows: list[dict[str, Any]]) -> dict[tuple[str, str], dict[str, dict[str, Any]]]:
    out: dict[tuple[str, str], dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in rows:
        out[(row["event"], row["market"])][row["segment"]] = row
    return out


def daily_from_activity_raw(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    daily: dict[tuple[str, str], dict[str, Any]] = {}
    for row in rows:
        raw_path = Path(row["rawPath"])
        fills = load_json(raw_path)
        for f in fills:
            d = datetime.fromtimestamp(int(f["time"]) / 1000, tz=timezone.utc).date().isoformat()
            key = (row["label"], d)
            rec = daily.setdefault(
                key,
                {"market": row["label"], "date_utc": d, "fill_count": 0, "notional_usd": 0.0, "opening_fees_usd": 0.0, "total_fees_usd": 0.0},
            )
            rec["fill_count"] += 1
            rec["notional_usd"] += abs(float(f.get("px") or 0) * float(f.get("szi") or 0))
            fees = f.get("fees") or {}
            rec["opening_fees_usd"] += float(fees.get("opening") or 0)
            rec["total_fees_usd"] += sum(float(v or 0) for v in fees.values())
    return sorted(daily.values(), key=lambda r: (r["market"], r["date_utc"]))


def social_baseline_apr13() -> dict[str, Any]:
    baseline_path = LEGACY_BASELINE / "raw_x_ostium_all_pm7d_canonical.json"
    if not baseline_path.exists():
        raise FileNotFoundError("Historical v1 baseline fixture is not included in the public package; use the v1.3/v1.4 cached pipeline instead.")
    posts = read_posts(baseline_path)
    canon = next(r for r in posts if r["tweet_id"] == EVENTS["apr13_canonical"]["tweet_id"])
    baseline = [r for r in posts if r["tweet_id"] != canon["tweet_id"] and not r["is_oil"]]
    med_imp = safe_median(r["impressions"] for r in baseline)
    med_eng = safe_median(r["engagement_count"] for r in baseline)
    return {
        "post_count": len(posts),
        "non_oil_baseline_count": len(baseline),
        "canonical_impressions": canon["impressions"],
        "canonical_engagement": canon["engagement_count"],
        "non_oil_median_impressions": med_imp,
        "non_oil_median_engagement": med_eng,
        "impressions_vs_baseline_pct": pct_change(canon["impressions"], med_imp or 0),
        "engagement_vs_baseline_pct": pct_change(canon["engagement_count"], med_eng or 0),
    }


def social_baseline_mar_cluster() -> dict[str, Any]:
    summary_path = LEGACY_BASELINE / "ostium_mar9_10_cluster_pm7_summary.json"
    if not summary_path.exists():
        raise FileNotFoundError("Historical v1 baseline fixture is not included in the public package; use the v1.3/v1.4 cached pipeline instead.")
    summary = load_json(summary_path)
    return summary


def activity_response_rows(activity_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped = activity_by_event_market(activity_rows)
    out = []
    for (event, market), segs in sorted(grouped.items()):
        pre = segs.get("pre7", {})
        ev = segs.get("event", {})
        post = segs.get("post7", {})
        pre_days = 7
        ev_days = 1 if event == "apr13_canonical" else 2
        post_days = 7
        def per_day(seg: dict[str, Any], field: str, days: int) -> float:
            return float(seg.get(field) or 0) / days
        row = {
            "event": event,
            "market": market,
            "pre_notional_per_day": per_day(pre, "notional_usd", pre_days),
            "event_notional_per_day": per_day(ev, "notional_usd", ev_days),
            "post_notional_per_day": per_day(post, "notional_usd", post_days),
            "event_vs_pre_notional_pct": pct_change(per_day(ev, "notional_usd", ev_days), per_day(pre, "notional_usd", pre_days)),
            "post_vs_pre_notional_pct": pct_change(per_day(post, "notional_usd", post_days), per_day(pre, "notional_usd", pre_days)),
            "pre_fills_per_day": per_day(pre, "fill_count", pre_days),
            "event_fills_per_day": per_day(ev, "fill_count", ev_days),
            "post_fills_per_day": per_day(post, "fill_count", post_days),
            "event_vs_pre_fills_pct": pct_change(per_day(ev, "fill_count", ev_days), per_day(pre, "fill_count", pre_days)),
            "post_vs_pre_fills_pct": pct_change(per_day(post, "fill_count", post_days), per_day(pre, "fill_count", pre_days)),
            "pre_opening_fees_per_day": per_day(pre, "opening_fees_usd", pre_days),
            "event_opening_fees_per_day": per_day(ev, "opening_fees_usd", ev_days),
            "post_opening_fees_per_day": per_day(post, "opening_fees_usd", post_days),
            "event_vs_pre_fees_pct": pct_change(per_day(ev, "opening_fees_usd", ev_days), per_day(pre, "opening_fees_usd", pre_days)),
            "post_vs_pre_fees_pct": pct_change(per_day(post, "opening_fees_usd", post_days), per_day(pre, "opening_fees_usd", pre_days)),
        }
        out.append(row)
    return out


def build_report(oil_posts: list[dict[str, Any]], activity_rows: list[dict[str, Any]], response_rows: list[dict[str, Any]]) -> str:
    apr_social = social_baseline_apr13()
    mar_social = social_baseline_mar_cluster()
    resp = {(r["event"], r["market"]): r for r in response_rows}
    total_impressions = sum(r["impressions"] for r in oil_posts)
    top = sorted(oil_posts, key=lambda r: r["impressions"], reverse=True)[:5]

    lines: list[str] = []
    lines.append("# Ostium Oil/Hormuz V1 Report")
    lines.append("")
    lines.append("Date: 2026-05-11")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append("This v1 joins official `@Ostium` oil-related X posts, Ostium Builder OHLC, DefiLlama aggregate protocol proxies, and read-only Ostium SDK per-market fills for WTI and Brent. No Dune was used.")
    lines.append("")
    lines.append("## Source coverage")
    lines.append("")
    lines.append(f"- X oil-post sample: {len(oil_posts)} posts; total impressions {total_impressions:,}.")
    lines.append("- SDK activity: `OstiumClient.createReadOnly()` + `getFillsByTime({ user: 'ALL', pairId, ... })`.")
    lines.append("- Pair mapping: WTI/CL pairId `7`; Brent pairId `55`.")
    lines.append("- Activity metric validation: SDK `Fill.px` is execution price and `Fill.szi` is documented trade size in base-asset units; SDK source maps `tradeNotional` to `szi`. Therefore `abs(px * szi)` is used as USD execution notional for WTI/Brent fills.")
    lines.append("")
    lines.append("## Event 1 — Apr 13 canonical Hormuz/oil-shock post")
    lines.append("")
    lines.append(f"Social baseline: canonical post had {apr_social['canonical_impressions']:,} impressions and {apr_social['canonical_engagement']} engagement vs ±7d non-oil medians of {apr_social['non_oil_median_impressions']:,.0f} impressions and {apr_social['non_oil_median_engagement']:,.0f} engagement.")
    lines.append(f"- Impression lift vs non-oil median: {pct(apr_social['impressions_vs_baseline_pct'])}.")
    lines.append(f"- Engagement lift vs non-oil median: {pct(apr_social['engagement_vs_baseline_pct'])}.")
    for market in ["WTI", "BRENT"]:
        r = resp[("apr13_canonical", market)]
        lines.append(f"- {market} SDK activity: event notional/day {money(r['event_notional_per_day'])} vs pre7/day {money(r['pre_notional_per_day'])} ({pct(r['event_vs_pre_notional_pct'])}); post7/day {money(r['post_notional_per_day'])} ({pct(r['post_vs_pre_notional_pct'])}).")
        lines.append(f"  - fills/day: event {r['event_fills_per_day']:.1f} vs pre7 {r['pre_fills_per_day']:.1f} ({pct(r['event_vs_pre_fills_pct'])}). opening fees/day: event {money(r['event_opening_fees_per_day'])} vs pre7 {money(r['pre_opening_fees_per_day'])} ({pct(r['event_vs_pre_fees_pct'])}).")
    lines.append("Interpretation: strong social outperformance, but per-market activity is lower than the preceding week for both WTI and Brent. This supports the earlier aggregate finding: Apr 13 is a social-performance case, not a clear protocol-activity-lift case.")
    lines.append("")
    lines.append("## Event 2 — Mar 9–10 oil/Hormuz cluster")
    lines.append("")
    lines.append(f"Social baseline: oil-cluster median impressions {mar_social['cluster_oil_median_impressions']:,.0f} vs non-oil baseline {mar_social['baseline_non_oil_median_impressions']:,.0f}; median engagement {mar_social['cluster_oil_median_engagement']:,.0f} vs baseline {mar_social['baseline_non_oil_median_engagement']:,.0f}.")
    lines.append(f"- Impression delta vs non-oil median: {pct(mar_social['cluster_vs_baseline_impressions_pct'])}.")
    lines.append(f"- Engagement delta vs non-oil median: {pct(mar_social['cluster_vs_baseline_engagement_pct'])}.")
    for market in ["WTI", "BRENT"]:
        r = resp[("mar9_10_cluster", market)]
        lines.append(f"- {market} SDK activity: event notional/day {money(r['event_notional_per_day'])} vs pre7/day {money(r['pre_notional_per_day'])} ({pct(r['event_vs_pre_notional_pct'])}); post7/day {money(r['post_notional_per_day'])} ({pct(r['post_vs_pre_notional_pct'])}).")
        lines.append(f"  - fills/day: event {r['event_fills_per_day']:.1f} vs pre7 {r['pre_fills_per_day']:.1f} ({pct(r['event_vs_pre_fills_pct'])}). opening fees/day: event {money(r['event_opening_fees_per_day'])} vs pre7 {money(r['pre_opening_fees_per_day'])} ({pct(r['event_vs_pre_fees_pct'])}).")
    lines.append("Interpretation: not a social median-outperformance case, but WTI activity was materially elevated per day during the cluster. Brent had no fills in the tested window, so the activity signal is WTI-specific.")
    lines.append("")
    lines.append("## Top oil posts by impressions")
    lines.append("")
    for r in top:
        lines.append(f"- {r['created_at'][:10]} — {r['impressions']:,} impressions — {r['url']} — {r['text']}")
    lines.append("")
    lines.append("## Bottom-line v1 read")
    lines.append("")
    lines.append("- **Apr 13:** social signal strong; per-market activity response weak/negative vs pre-window.")
    lines.append("- **Mar 9–10:** social median signal weak; WTI per-market activity strong and aligns with the protocol-fee spike previously observed.")
    lines.append("- The likely distinction is useful: some posts are high-engagement narrative posts, while others appear reactive/coincident with actual market-specific trading activity.")
    lines.append("- Causality is still not established; v1 supports event-window correlation only.")
    lines.append("")
    lines.append("## Generated files")
    lines.append("")
    lines.append(f"- `{rel(REPORTS / 'ostium-oil-hormuz-v1.md')}`")
    lines.append(f"- `{rel(REPORTS / 'ostium-oil-hormuz-event-table.csv')}`")
    lines.append(f"- `{rel(PROCESSED / 'activity_windows.csv')}`")
    lines.append(f"- `{rel(PROCESSED / 'activity_daily.csv')}`")
    lines.append(f"- `{rel(PROCESSED / 'activity_response.csv')}`")
    return "\n".join(lines) + "\n"


def main() -> None:
    oil_posts = read_posts(RAW / "social" / "x_ostium_oil_90d.json")
    activity_windows_raw = load_activity_windows()
    activity_rows = normalize_activity_windows(activity_windows_raw)
    daily_rows = daily_from_activity_raw(activity_windows_raw)
    response_rows = activity_response_rows(activity_rows)

    write_csv(PROCESSED / "oil_posts.csv", oil_posts)
    write_csv(PROCESSED / "activity_windows.csv", activity_rows)
    write_csv(PROCESSED / "activity_daily.csv", daily_rows)
    write_csv(PROCESSED / "activity_response.csv", response_rows)

    # Event table is intentionally compact for review.
    event_rows = []
    for r in response_rows:
        event_rows.append(r)
    write_csv(REPORTS / "ostium-oil-hormuz-event-table.csv", event_rows)

    report = build_report(oil_posts, activity_rows, response_rows)
    (REPORTS / "ostium-oil-hormuz-v1.md").write_text(report)
    print(json.dumps({
        "report": rel(REPORTS / "ostium-oil-hormuz-v1.md"),
        "event_table": rel(REPORTS / "ostium-oil-hormuz-event-table.csv"),
        "oil_posts": len(oil_posts),
        "activity_windows": len(activity_rows),
        "daily_activity_rows": len(daily_rows),
    }, indent=2))


if __name__ == "__main__":
    main()
