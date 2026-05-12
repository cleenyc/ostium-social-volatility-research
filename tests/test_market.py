from datetime import date

from ostium_social_volatility.market import (
    MarketDay,
    average_metric,
    event_study_lift,
    pct_return,
    range_pct,
    window_days,
)


def test_daily_price_metrics_are_percent_units():
    assert pct_return(105, 100) == 5.0
    assert pct_return(95, 100) == -5.0
    assert pct_return(100, 0) is None
    assert range_pct(high=110, low=90, open_=100) == 20.0


def test_window_days_includes_event_day_through_two_days_after():
    assert window_days(date(2026, 4, 13), 0, 2) == [
        date(2026, 4, 13),
        date(2026, 4, 14),
        date(2026, 4, 15),
    ]


def test_average_metric_ignores_missing_market_days():
    rows = [
        MarketDay(date=date(2026, 4, 13), symbol="WTI", open=100, high=110, low=90, close=105),
        MarketDay(date=date(2026, 4, 14), symbol="WTI", open=105, high=108, low=102, close=103),
    ]
    assert round(average_metric(rows, "abs_return_pct"), 3) == 3.452
    assert round(average_metric(rows, "range_pct"), 3) == 12.857


def test_event_study_lift_uses_rolling_baseline_and_primary_window():
    baseline = [MarketDay(date=date(2026, 4, d), symbol="WTI", open=100, high=102, low=98, close=101) for d in range(1, 11)]
    event = [MarketDay(date=date(2026, 4, d), symbol="WTI", open=100, high=112, low=94, close=110) for d in range(13, 16)]
    lift = event_study_lift(event, baseline, metric="range_pct")
    assert lift["baseline_avg"] == 4.0
    assert lift["event_avg"] == 18.0
    assert lift["lift_pct"] == 350.0
    assert lift["baseline_observations"] == 10
    assert lift["event_observations"] == 3
