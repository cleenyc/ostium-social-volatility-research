# Reproducibility Guide

This guide describes the public/cached reproduction path for the oil/Hormuz reference study.

## Reference study

- Study config: `configs/study.oil-hormuz.example.yaml`
- Social fixture: `data/raw/social/x_ostium_oil_90d.json`
- Market OHLC fixtures: `data/raw/market_ohlc/`
- Ostium activity fixtures: `data/raw/event_study_activity_windows/` and `data/raw/volatility_control_activity_windows/`
- Main outputs: `reports/ostium-oil-hormuz-event-study-v1_3.*`, `reports/ostium-oil-hormuz-volatility-control-v1_4.*`, and `dashboard/data/summary.json`

## Environment

```bash
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -e '.[dev]'
npm install
```

The npm scripts use `python` through the active environment when possible. If your environment requires an explicit Python path, run the Python commands directly with `PYTHONPATH=src`.

## Cached rerun commands

Validate existing cached artifacts:

```bash
PYTHONPATH=src python3 -m ostium_social_volatility validate --study configs/study.oil-hormuz.example.yaml
```

Regenerate cached reports:

```bash
PYTHONPATH=src python3 -m ostium_social_volatility report --study configs/study.oil-hormuz.example.yaml
```

Run reports and validation together:

```bash
PYTHONPATH=src python3 -m ostium_social_volatility run --study configs/study.oil-hormuz.example.yaml --mode cached
```

Regenerate dashboard data:

```bash
PYTHONPATH=src python3 scripts/build_dashboard_data.py --study configs/study.oil-hormuz.example.yaml --out-dir dashboard/data
```

Run tests:

```bash
PYTHONPATH=src python3 -m pytest -q
```

## Expected fixture counts

The committed oil/Hormuz snapshot is expected to validate these fixture-level counts:

- Event-study posts: 29.
- Unique post dates: 21.
- WTI eligible volatility-control days: 75.
- Brent eligible volatility-control days: 26.
- High-volatility control rows: 30 total across WTI and Brent under the default 75th-percentile threshold.

## Live data collection

High-level live mode is intentionally disabled for now:

```bash
PYTHONPATH=src python3 -m ostium_social_volatility run --study configs/study.oil-hormuz.example.yaml --mode live
# exits with a warning/error instead of silently collecting live data
```

To adapt the project to a new topic, use `docs/adapt-study.md`. A future live path should explicitly document:

- X/Twitter API or `xurl` access;
- search tier/date-window limitations;
- Ostium SDK availability and pair IDs;
- OHLC source and redistribution constraints;
- rate limits, costs, and failure modes;
- where raw and processed outputs are written.
