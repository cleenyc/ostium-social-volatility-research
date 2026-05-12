from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_phase2_collectors_accept_study_config_and_avoid_chris_local_post_path():
    event_collector = (ROOT / "scripts" / "collect_event_study_activity_windows.mjs").read_text()
    control_collector = (ROOT / "scripts" / "collect_volatility_control_activity_windows.mjs").read_text()

    assert "--study" in event_collector
    assert "--study" in control_collector
    assert "project-artifacts/ostium-social-volatility-backtest" not in event_collector
    assert "configs/study.oil-hormuz.example.yaml" in event_collector
    assert "configs/study.oil-hormuz.example.yaml" in control_collector
