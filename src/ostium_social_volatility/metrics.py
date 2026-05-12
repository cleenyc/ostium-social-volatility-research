from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from statistics import median
from typing import Any, Iterable

# Keep this deliberately narrow to reproduce the established baseline notes.
# Broader tags such as "energy" or ticker-like "CL" can be added in a later
# classifier pass, but they change the non-oil baseline denominator.
OIL_TERMS = ("oil", "crude", "brent", "wti", "hormuz")


def engagement_count(metrics: dict[str, Any]) -> int:
    return sum(int(metrics.get(k) or 0) for k in ["retweet_count", "reply_count", "like_count", "quote_count", "bookmark_count"])


def impression_count(metrics: dict[str, Any]) -> int:
    return int(metrics.get("impression_count") or 0)


def is_oil_text(text: str) -> bool:
    lower = f" {text.lower()} "
    return any(term in lower for term in OIL_TERMS)


def post_type(post: dict[str, Any]) -> str:
    text = post.get("text") or ""
    if text.startswith("RT @"):
        return "retweet"
    if (post.get("conversation_id") and post.get("conversation_id") != post.get("id")) or text.startswith("@"):
        return "reply"
    return "original"


def oil_categories(text: str) -> list[str]:
    lower = text.lower()
    cats = []
    if "hormuz" in lower:
        cats.append("hormuz")
    if "brent" in lower:
        cats.append("brent")
    if "wti" in lower or " cl" in lower or "$cl" in lower:
        cats.append("wti_cl")
    if "crude" in lower:
        cats.append("crude")
    if "oil" in lower:
        cats.append("oil")
    return cats or (["oil_other"] if is_oil_text(text) else [])


def dt_from_x(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def fill_notional(fill: dict[str, Any]) -> float:
    """USD notional from Ostium SDK fill `px * szi`.

    Validation source: @ostium/builder-sdk `Fill.szi` is documented as
    "Trade size in base-asset units at the time of execution" and `Fill.px` is
    the execution price. The SDK formatter maps subgraph `tradeNotional` to
    `szi` and also computes price-impact fee as `(px - pxBeforeImpact) * szi`.
    Therefore `abs(px * szi)` is the USD execution notional for WTI/Brent fills.
    """
    return abs(float(fill.get("px") or 0) * float(fill.get("szi") or 0))


def fill_fee_sum(fill: dict[str, Any]) -> float:
    fees = fill.get("fees") or {}
    return sum(float(v or 0) for v in fees.values())


def summarize_fills(fills: Iterable[dict[str, Any]]) -> dict[str, Any]:
    rows = list(fills)
    actions = Counter(str(f.get("action") or "unknown") for f in rows)
    sides = Counter(str(f.get("side") or "unknown") for f in rows)
    return {
        "fill_count": len(rows),
        "notional_usd": sum(fill_notional(f) for f in rows),
        "opening_fees_usd": sum(float((f.get("fees") or {}).get("opening") or 0) for f in rows),
        "total_fees_usd": sum(fill_fee_sum(f) for f in rows),
        "actions": dict(actions),
        "sides": dict(sides),
    }


def pct_change(current: float, baseline: float) -> float | None:
    if baseline == 0:
        return None
    return (current - baseline) / baseline * 100.0


def safe_median(values: Iterable[float]) -> float | None:
    vals = list(values)
    return float(median(vals)) if vals else None
