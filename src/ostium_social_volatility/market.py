from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from statistics import mean, pstdev
from typing import Iterable, Literal

MetricName = Literal["return_pct", "abs_return_pct", "range_pct"]


@dataclass(frozen=True)
class MarketDay:
    date: date
    symbol: str
    open: float
    high: float
    low: float
    close: float

    @property
    def return_pct(self) -> float | None:
        return pct_return(self.close, self.open)

    @property
    def abs_return_pct(self) -> float | None:
        r = self.return_pct
        return abs(r) if r is not None else None

    @property
    def range_pct(self) -> float | None:
        return range_pct(self.high, self.low, self.open)


def pct_return(close: float, open_: float) -> float | None:
    if open_ == 0:
        return None
    return (close - open_) / open_ * 100.0


def range_pct(high: float, low: float, open_: float) -> float | None:
    if open_ == 0:
        return None
    return (high - low) / open_ * 100.0


def window_days(event_date: date, start_offset: int, end_offset: int) -> list[date]:
    return [event_date + timedelta(days=i) for i in range(start_offset, end_offset + 1)]


def metric_value(row: MarketDay, metric: MetricName) -> float | None:
    return getattr(row, metric)


def average_metric(rows: Iterable[MarketDay], metric: MetricName) -> float | None:
    vals = [metric_value(r, metric) for r in rows]
    clean = [float(v) for v in vals if v is not None]
    return mean(clean) if clean else None


def pct_lift(current: float | None, baseline: float | None) -> float | None:
    if current is None or baseline in (None, 0):
        return None
    return (current - baseline) / baseline * 100.0


def z_score(current: float | None, baseline_values: Iterable[float | None]) -> float | None:
    vals = [float(v) for v in baseline_values if v is not None]
    if current is None or len(vals) < 2:
        return None
    sd = pstdev(vals)
    if sd == 0:
        return None
    return (current - mean(vals)) / sd


def percentile_rank(current: float | None, baseline_values: Iterable[float | None]) -> float | None:
    vals = sorted(float(v) for v in baseline_values if v is not None)
    if current is None or not vals:
        return None
    less_or_equal = sum(1 for v in vals if v <= current)
    return less_or_equal / len(vals) * 100.0


def event_study_lift(event_rows: Iterable[MarketDay], baseline_rows: Iterable[MarketDay], metric: MetricName) -> dict[str, float | int | None]:
    event_list = list(event_rows)
    baseline_list = list(baseline_rows)
    event_avg = average_metric(event_list, metric)
    baseline_avg = average_metric(baseline_list, metric)
    baseline_values = [metric_value(r, metric) for r in baseline_list]
    return {
        "baseline_avg": baseline_avg,
        "event_avg": event_avg,
        "lift_pct": pct_lift(event_avg, baseline_avg),
        "z_score": z_score(event_avg, baseline_values),
        "percentile": percentile_rank(event_avg, baseline_values),
        "baseline_observations": len([v for v in baseline_values if v is not None]),
        "event_observations": len([metric_value(r, metric) for r in event_list if metric_value(r, metric) is not None]),
    }
