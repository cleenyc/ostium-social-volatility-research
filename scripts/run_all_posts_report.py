#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median
from typing import Any

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from ostium_social_volatility.metrics import engagement_count, impression_count, oil_categories, pct_change, post_type

RAW = REPO / "data" / "raw" / "all_post_activity_windows" / "all_post_activity_windows_summary.json"
PROCESSED = REPO / "data" / "processed"
REPORTS = REPO / "reports"
PROCESSED.mkdir(parents=True, exist_ok=True)
REPORTS.mkdir(parents=True, exist_ok=True)


def rel(path: Path) -> str:
    try:
        return path.relative_to(REPO).as_posix()
    except ValueError:
        return path.as_posix()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def money(x: float | int | None) -> str:
    return "n/a" if x is None else f"${x:,.0f}"


def pct(x: float | None) -> str:
    return "n/a" if x is None else f"{x:+.1f}%"


def one_line(text: str, n: int = 150) -> str:
    t = " ".join((text or "").replace("\n", " ").split())
    return t if len(t) <= n else t[: n - 1] + "…"


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    fields = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def per_day(window: dict[str, Any], field: str) -> float:
    return float(window.get(field) or 0) / float(window.get("days") or 1)


def build_rows(data: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    windows = {(w["date"], w["label"], w["segment"]): w for w in data["windows"]}
    table: list[dict[str, Any]] = []
    window_rows: list[dict[str, Any]] = []
    for w in data["windows"]:
        window_rows.append({
            "date_utc": w["date"],
            "market": w["label"],
            "segment": w["segment"],
            "start": w["start"],
            "end": w["end"],
            "is_partial": w["isPartial"],
            "fill_count": w["fillCount"],
            "notional_usd": w["notionalUsd"],
            "opening_fees_usd": w["openingFeesUsd"],
            "total_fees_usd": w["totalFeesUsd"],
            "actions_json": json.dumps(w.get("actions", {}), sort_keys=True),
            "sides_json": json.dumps(w.get("sides", {}), sort_keys=True),
        })
    for p in sorted(data["posts"], key=lambda r: r["created_at"]):
        metrics = p.get("public_metrics") or {}
        base = {
            "tweet_id": p["id"],
            "url": f"https://x.com/ostium/status/{p['id']}",
            "created_at": p["created_at"],
            "date_utc": p["date"],
            "post_type": post_type(p),
            "categories": ";".join(oil_categories(p.get("text", ""))),
            "text": one_line(p.get("text", ""), 220),
            "impressions": impression_count(metrics),
            "engagement_count": engagement_count(metrics),
        }
        row = dict(base)
        for market in ["WTI", "BRENT"]:
            pre = windows[(p["date"], market, "pre7")]
            ev = windows[(p["date"], market, "event")]
            post = windows[(p["date"], market, "post7")]
            pre_notional = per_day(pre, "notionalUsd")
            ev_notional = per_day(ev, "notionalUsd")
            post_notional = per_day(post, "notionalUsd")
            pre_fills = per_day(pre, "fillCount")
            ev_fills = per_day(ev, "fillCount")
            post_fills = per_day(post, "fillCount")
            row.update({
                f"{market}_event_notional_usd": ev["notionalUsd"],
                f"{market}_event_notional_per_day": ev_notional,
                f"{market}_pre7_notional_per_day": pre_notional,
                f"{market}_post7_notional_per_day": post_notional,
                f"{market}_event_vs_pre_notional_pct": pct_change(ev_notional, pre_notional),
                f"{market}_post_vs_pre_notional_pct": pct_change(post_notional, pre_notional),
                f"{market}_event_fills": ev["fillCount"],
                f"{market}_event_fills_per_day": ev_fills,
                f"{market}_pre7_fills_per_day": pre_fills,
                f"{market}_post7_fills_per_day": post_fills,
                f"{market}_event_vs_pre_fills_pct": pct_change(ev_fills, pre_fills),
                f"{market}_post_vs_pre_fills_pct": pct_change(post_fills, pre_fills),
                f"{market}_event_opening_fees_usd": ev["openingFeesUsd"],
                f"{market}_event_opening_fees_per_day": per_day(ev, "openingFeesUsd"),
                f"{market}_post7_partial": post["isPartial"],
            })
        table.append(row)
    return table, window_rows


def safe_median(vals: list[float]) -> float | None:
    return float(median(vals)) if vals else None


def build_report(table: list[dict[str, Any]], data: dict[str, Any]) -> str:
    type_counts = Counter(r["post_type"] for r in table)
    cat_counts = Counter(c for r in table for c in r["categories"].split(";") if c)
    total_impressions = sum(int(r["impressions"] or 0) for r in table)
    originals = [r for r in table if r["post_type"] == "original"]
    replies = [r for r in table if r["post_type"] == "reply"]
    top_impressions = sorted(table, key=lambda r: r["impressions"], reverse=True)[:7]
    top_wti_lift = sorted([r for r in table if r["WTI_event_vs_pre_notional_pct"] is not None], key=lambda r: r["WTI_event_vs_pre_notional_pct"], reverse=True)[:7]
    top_wti_event_notional = sorted(table, key=lambda r: r["WTI_event_notional_per_day"], reverse=True)[:7]
    partial_count = sum(1 for r in table if r["WTI_post7_partial"] or r["BRENT_post7_partial"])

    med_original_impressions = safe_median([r["impressions"] for r in originals])
    med_reply_impressions = safe_median([r["impressions"] for r in replies])
    med_original_wti_lift = safe_median([r["WTI_event_vs_pre_notional_pct"] for r in originals if r["WTI_event_vs_pre_notional_pct"] is not None])
    med_reply_wti_lift = safe_median([r["WTI_event_vs_pre_notional_pct"] for r in replies if r["WTI_event_vs_pre_notional_pct"] is not None])

    lines = []
    lines.append("# Ostium Oil/Hormuz All-Posts V1.1 Report")
    lines.append("")
    lines.append("Date: 2026-05-11")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append("This slice broadens the Project Builder v1 from two hand-picked events to all 29 `@Ostium` posts returned by the last-90-day full-archive `from:Ostium oil` query. It adds post-type classification, oil subcategories, and WTI/Brent SDK activity windows for every unique post date.")
    lines.append("")
    lines.append("## Coverage")
    lines.append("")
    lines.append(f"- Posts: {len(table)} across {len(set(r['date_utc'] for r in table))} unique dates.")
    lines.append(f"- Post types: {dict(type_counts)}.")
    lines.append(f"- Oil categories: {dict(cat_counts)}.")
    lines.append(f"- Total impressions: {total_impressions:,}.")
    lines.append(f"- SDK windows collected: {len(data['windows'])}; pairs: WTI pairId 7 and Brent pairId 55.")
    lines.append(f"- Partial post-7d windows: {partial_count} posts, because latest May 6 posts extend beyond collection date {data['generatedAt'][:10]}.")
    lines.append("")
    lines.append("## Type-level read")
    lines.append("")
    lines.append(f"- Originals: {len(originals)} posts; median impressions {med_original_impressions:,.0f}; median WTI event-vs-pre notional lift {pct(med_original_wti_lift)}.")
    lines.append(f"- Replies: {len(replies)} posts; median impressions {med_reply_impressions:,.0f}; median WTI event-vs-pre notional lift {pct(med_reply_wti_lift)}.")
    lines.append("- Interpretation: originals dominate reach, while replies are useful context but should be separable in downstream analysis.")
    lines.append("")
    lines.append("## Top posts by impressions")
    for r in top_impressions:
        lines.append(f"- {r['date_utc']} [{r['post_type']}] {r['impressions']:,} impressions; WTI event notional/day {money(r['WTI_event_notional_per_day'])}; WTI lift {pct(r['WTI_event_vs_pre_notional_pct'])}; {r['url']} — {r['text']}")
    lines.append("")
    lines.append("## Top WTI activity-lift dates/posts")
    for r in top_wti_lift:
        lines.append(f"- {r['date_utc']} [{r['post_type']}] WTI lift {pct(r['WTI_event_vs_pre_notional_pct'])}; event notional/day {money(r['WTI_event_notional_per_day'])}; impressions {r['impressions']:,}; {r['url']} — {r['text']}")
    lines.append("")
    lines.append("## Top WTI event-notional dates/posts")
    for r in top_wti_event_notional:
        lines.append(f"- {r['date_utc']} [{r['post_type']}] WTI event notional/day {money(r['WTI_event_notional_per_day'])}; WTI lift {pct(r['WTI_event_vs_pre_notional_pct'])}; impressions {r['impressions']:,}; {r['url']} — {r['text']}")
    lines.append("")
    lines.append("## Bottom-line v1.1 read")
    lines.append("")
    lines.append("- The all-post view reinforces that social reach and protocol activity are different signals.")
    lines.append("- May 6 dominates impressions due to the liquidity-engine post; its post-window is partial and should not be over-read yet.")
    lines.append("- The strongest protocol-activity windows remain WTI-heavy; Brent appears concentrated around launch/Apr 13 rather than Mar 9–10.")
    lines.append("- Next useful step is filtering to original posts only, then grouping adjacent post dates into clusters to avoid duplicate activity windows for same-day posts.")
    lines.append("")
    lines.append("## Generated files")
    lines.append("")
    lines.append(f"- `{rel(REPORTS / 'ostium-oil-hormuz-all-posts-v1_1.md')}`")
    lines.append(f"- `{rel(REPORTS / 'ostium-oil-hormuz-all-posts-event-table.csv')}`")
    lines.append(f"- `{rel(PROCESSED / 'all_post_activity_windows.csv')}`")
    return "\n".join(lines) + "\n"


def main() -> None:
    data = load_json(RAW)
    table, window_rows = build_rows(data)
    write_csv(PROCESSED / "all_post_activity_windows.csv", window_rows)
    write_csv(REPORTS / "ostium-oil-hormuz-all-posts-event-table.csv", table)
    report = build_report(table, data)
    (REPORTS / "ostium-oil-hormuz-all-posts-v1_1.md").write_text(report)
    print(json.dumps({
        "report": rel(REPORTS / "ostium-oil-hormuz-all-posts-v1_1.md"),
        "event_table": rel(REPORTS / "ostium-oil-hormuz-all-posts-event-table.csv"),
        "posts": len(table),
        "unique_dates": len(set(r["date_utc"] for r in table)),
        "windows": len(window_rows),
    }, indent=2))


if __name__ == "__main__":
    main()
