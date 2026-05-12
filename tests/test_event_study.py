from ostium_social_volatility.event_study import lift_vs_baseline, per_day_value


def test_per_day_value_normalizes_window_totals():
    assert per_day_value({"notionalUsd": 300, "days": 3}, "notionalUsd") == 100
    assert per_day_value({"fillCount": 0, "days": 0}, "fillCount") == 0


def test_lift_vs_baseline_handles_zero_baseline():
    result = lift_vs_baseline(event_value=150, baseline_value=100)
    assert result == 50
    assert lift_vs_baseline(event_value=10, baseline_value=0) is None
