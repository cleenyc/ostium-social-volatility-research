from __future__ import annotations

from typing import Any


def per_day_value(window: dict[str, Any], field: str) -> float:
    days = float(window.get("days") or 0)
    if days == 0:
        return 0.0
    return float(window.get(field) or 0) / days


def lift_vs_baseline(event_value: float | None, baseline_value: float | None) -> float | None:
    if event_value is None or baseline_value in (None, 0):
        return None
    return (event_value - baseline_value) / baseline_value * 100.0
