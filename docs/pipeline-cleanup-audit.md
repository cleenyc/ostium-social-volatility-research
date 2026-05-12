# Pipeline Cleanup Audit — Ostium Social Volatility Research Kit

Date: 2026-05-12  
Status: pipeline cleanup reproducibility audit draft  
Scope: Reproducible pipeline cleanup, not dashboard/skill/public packaging

## pipeline cleanup Objective

Agreed pipeline cleanup objective:

> Make inputs, config, data, and source pipeline clean enough for others.

Agreed deliverables:

- canonical config schema;
- repeatable commands;
- cleaned scripts;
- raw/processed data contract;
- source-access docs;
- validation checks.

This document audits the current local research repo against that objective.

## Current Pipeline Inventory

### Main v1.3 event-study pipeline

Current commands:

```bash
node scripts/collect_event_study_activity_windows.mjs
python3 scripts/run_event_study_report.py
```

Current inputs:

- X posts source: `local-provenance/2026-05-11-readonly-spike/raw_x_ostium_oil_90d.json`
- OHLC source copies from: `local-provenance/2026-05-11-readonly-spike/CL-USD_daily_ohlc.csv`
- OHLC source copies from: `local-provenance/2026-05-11-readonly-spike/BRENT-USD_daily_ohlc.csv`
- SDK activity raw output: `data/raw/event_study_activity_windows/event_study_activity_windows_summary.json`

Current outputs:

- `reports/ostium-oil-hormuz-event-study-v1_3.md`
- `reports/ostium-oil-hormuz-event-study-v1_3.csv`
- `data/processed/market_volatility_event_windows.csv`
- `data/processed/event_study_activity_windows.csv`

Current strengths:

- Produces the main post-level event-study outputs.
- Includes exact post-time +48h/+72h activity windows.
- Uses read-only SDK activity, not paid Dune.
- Generates deterministic reports from cached/raw activity outputs after collection.

Current cleanup gaps:

- Earlier draft had a hardcoded local project-artifacts source path; public scripts now use repo-relative fixture paths.
- Hardcoded markets/pair IDs inside JS and Python scripts.
- Hardcoded output filenames and version names.
- No single study config controls query/date/markets/windows.
- No validation command verifies row counts, required columns, and critical non-empty windows.
- Python command is environment-specific (`python3`) rather than portable.

### Main v1.4 volatility-control pipeline

Current commands:

```bash
node scripts/collect_volatility_control_activity_windows.mjs
python3 scripts/run_volatility_control_report.py
```

Current inputs:

- OHLC CSVs from `data/raw/market_ohlc/`.
- v1.3 event table: `reports/ostium-oil-hormuz-event-study-v1_3.csv`.
- SDK activity windows: `data/raw/volatility_control_activity_windows/volatility_control_activity_windows_summary.json`.

Current outputs:

- `reports/ostium-oil-hormuz-volatility-control-v1_4.md`
- `reports/ostium-oil-hormuz-volatility-control-v1_4.csv`
- `data/processed/volatility_control_days.csv`

Current strengths:

- Adds the missing high-volatility post vs no-post control group.
- Encodes the current headline result.
- Has clear high-volatility defaults: range lift > 0 and percentile >= 75.

Current cleanup gaps:

- High-vol threshold and minimum baseline observations are constants in script, not config.
- Markets and pair IDs are hardcoded.
- Depends on the v1.3 CSV existing in a specific report path.
- Does not expose a reusable command interface such as `run --study configs/study.yaml --stage control`.
- Validation is implicit; report generation fails on some missing data, but there is no structured validator.

### Earlier v1/v1.1 pipelines

Scripts:

- `scripts/collect_activity_windows.mjs`
- `scripts/run_oil_hormuz_report.py`
- `scripts/collect_all_post_activity_windows.mjs`
- `scripts/run_all_posts_report.py`
- `scripts/smoke_ostium_activity.mjs`
- `scripts/smoke_ostium_activity.py`

Current role:

- Historical iteration sources.
- Useful for provenance and smoke tests.
- Not the preferred rerun surface for the public research kit.

pipeline cleanup recommendation:

- Preserve for history, but do not make them the default user-facing commands.
- Fold reusable pieces into a canonical collect/process/report/validate command path.

## Current Source Modules

Existing Python package modules:

- `src/ostium_social_volatility/config.py`
- `src/ostium_social_volatility/event_study.py`
- `src/ostium_social_volatility/market.py`
- `src/ostium_social_volatility/metrics.py`

Current tests:

- `tests/test_config.py`
- `tests/test_event_study.py`
- `tests/test_market.py`
- `tests/test_metrics.py`

Strengths:

- Basic reusable metric and market functions exist.
- Existing tests cover some calculations.

Gaps:

- `config.py` is currently constants-only and oil-specific.
- No config loader for study YAML/JSON.
- No schema/data contract validation module.
- No source collector abstraction for `xurl` vs raw X API.
- No unified CLI entrypoint.

## Current Data Inventory

### Raw data

Important current raw files:

- `data/raw/event_study_activity_windows/event_study_activity_windows_summary.json`
- `data/raw/volatility_control_activity_windows/volatility_control_activity_windows_summary.json`
- `data/raw/market_ohlc/CL-USD_daily_ohlc.csv`
- `data/raw/market_ohlc/BRENT-USD_daily_ohlc.csv`
- `data/raw/source_smoke/*`
- `data/raw/activity_windows/*`

Issue:

- Some early raw X provenance inputs lived outside the repo; the public cached fixture now lives under `data/raw/social/`.
- Public repo version should avoid requiring Chris-local absolute paths.

### Processed data

Important current processed files:

- `data/processed/oil_posts.csv`
- `data/processed/activity_windows.csv`
- `data/processed/activity_daily.csv`
- `data/processed/activity_response.csv`
- `data/processed/all_post_activity_windows.csv`
- `data/processed/market_volatility_event_windows.csv`
- `data/processed/event_study_activity_windows.csv`
- `data/processed/volatility_control_days.csv`

Issue:

- Contracts for each CSV are not documented centrally.
- Required columns are not validated by a single command.

## pipeline cleanup Target State

### Config-first execution

A study should be runnable from a single config file:

```bash
python -m ostium_social_volatility run --study configs/study.oil-hormuz.yaml
```

Or by explicit stages:

```bash
python -m ostium_social_volatility collect --study configs/study.oil-hormuz.yaml
python -m ostium_social_volatility process --study configs/study.oil-hormuz.yaml
python -m ostium_social_volatility report --study configs/study.oil-hormuz.yaml
python -m ostium_social_volatility validate --study configs/study.oil-hormuz.yaml
```

Node SDK collection can remain under the hood, but the public command surface should not require users to know the internal script order.

### Clean config schema

The config must define:

- study metadata;
- X source config;
- market definitions;
- classification terms;
- event windows;
- baseline windows;
- volatility thresholds;
- output paths;
- public/export settings.

See: `configs/study.oil-hormuz.example.yaml`.

### Raw and processed contracts

The repo should document and validate:

- raw X posts JSON;
- normalized posts CSV;
- raw OHLC CSV;
- normalized market volatility CSV;
- raw SDK activity windows JSON;
- processed activity windows CSV;
- event-study output CSV;
- volatility-control output CSV.

See: `docs/data-contracts.md`.

### Validation checks

Minimum validation command should check:

- config parses;
- market symbols and pair IDs are present;
- required raw files exist when running cached mode;
- required output columns exist;
- expected row-count lower bounds are satisfied;
- no critical metric columns are entirely empty;
- high-volatility filter reproduces expected WTI/Brent counts for fixture data;
- no secret-like files are inside output/public-export paths.

### Source access docs

Source docs should state:

- X full-archive access required for historical reruns;
- `xurl` recent-search shortcut is not enough for history;
- raw X API path should be supported;
- Ostium Builder API symbols must be discovered from Ostium source, not guessed;
- Ostium SDK pair IDs must be confirmed before activity collection.

## Recommended pipeline cleanup Implementation Slices

### Slice 2.1 — Config schema and example config

Deliverables:

- `configs/study.oil-hormuz.example.yaml`
- `docs/pipeline-cleanup-audit.md`
- `docs/data-contracts.md`

No risky external calls.

### Slice 2.2 — Data contract validator

Deliverables:

- `src/ostium_social_volatility/validate.py`
- `scripts/validate_pipeline.py`
- tests for required columns and row counts.

### Slice 2.3 — Command surface wrapper

Deliverables:

- `src/ostium_social_volatility/cli.py` or simple script wrapper.
- Commands: `validate`, `report`, possibly `run-cached` first.

### Slice 2.4 — Remove local absolute path dependency

Deliverables:

- move or document raw X fixture location;
- make source path configurable;
- make event-study collection read from config.

### Slice 2.5 — Cached rerun proof

Deliverables:

- run from saved raw/cache data;
- regenerate v1.3/v1.4 outputs;
- compare headline metrics to expected values;
- document proof in pipeline cleanup status.

## What pipeline cleanup Is Not

pipeline cleanup is not:

- building the visual dashboard;
- creating the public GitHub repo;
- deploying to Vercel;
- writing the Hermes skill package;
- building the live recommendation engine.

Those belong to later phases.
