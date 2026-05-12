# Repeatable Command Surface

Date: 2026-05-12  
Status: Draft command design for reproducible pipeline cleanup

## Purpose

The current repo can reproduce v1.3 and v1.4 through a simpler command surface that another user or agent can follow.

This document defines the target command interface and maps it to current scripts.

## Current Commands

Implemented cached run command:

```bash
PYTHONPATH=src python3 -m ostium_social_volatility run --study configs/study.oil-hormuz.example.yaml --mode cached
# or
npm run run:cached
```

This command regenerates the v1.3 event-study report and v1.4 volatility-control report from cached/raw inputs, then runs validation. Current verified output: v1.3 posts `29`, unique dates `21`, market windows `84`, activity windows `342`; v1.4 rows `101`, high-volatility rows `30`, WTI eligible days `75`, Brent eligible days `26`; validation `23 ok, 0 warn, 0 fail`.

Implemented report-only command:

```bash
PYTHONPATH=src python3 -m ostium_social_volatility report --study configs/study.oil-hormuz.example.yaml
# or
npm run report
```

Implemented validator command:

```bash
PYTHONPATH=src python3 -m ostium_social_volatility validate --study configs/study.oil-hormuz.example.yaml
# or
python3 scripts/validate_pipeline.py --study configs/study.oil-hormuz.example.yaml
# or
npm run validate
```

The validator currently checks cached v1.3/v1.4 artifacts, required columns, optional fixture expectations, volatility-control high-volatility counts, processed/report CSV parity, and configured public-safety path patterns. Exact oil/Hormuz counts now live under `validation.fixture_expectations`; portable new-study configs can omit that section so counts are observed rather than enforced.

The v1.4 volatility-control report script now accepts the same study config for its paths, markets, volatility threshold, and minimum baseline observations:

```bash
PYTHONPATH=src python3 scripts/run_volatility_control_report.py --study configs/study.oil-hormuz.example.yaml
```

A rerun produced byte-identical v1.4 CSV/Markdown artifacts against the prior cached outputs.

From the current repo README:

```bash
# Collect V1.3 event-study activity windows and generate event-study report
node scripts/collect_event_study_activity_windows.mjs
python3 scripts/run_event_study_report.py

# Collect V1.4 volatility-day control windows and generate control report
node scripts/collect_volatility_control_activity_windows.mjs
python3 scripts/run_volatility_control_report.py

# Run tests
python3 -m pytest -q
```

Current issues:

- Python path is local/Hermes-specific.
- Commands are version-specific rather than study/config-specific.
- Collection/report ordering is not enforced.
- No one command validates all expected outputs.
- No one command reruns the complete pipeline.

## Target User-Facing Commands

### 1. Validate environment and config

```bash
python -m ostium_social_volatility validate --study configs/study.oil-hormuz.example.yaml
```

Purpose:

- parse config;
- verify required local dependencies;
- verify required cached inputs or live source credentials depending on mode;
- verify no obvious secret files are in output paths;
- verify pair IDs and market symbols are configured.

### 2. Collect raw data

```bash
python -m ostium_social_volatility collect --study configs/study.oil-hormuz.example.yaml
```

Purpose:

- collect social posts;
- collect market OHLC;
- collect SDK activity windows;
- save raw/cached source files.

Implementation note:

- This Python command can shell out to Node SDK scripts internally if needed.
- Long term, the user should not need to know whether the collector is Python or Node.

### 3. Process normalized tables

```bash
python -m ostium_social_volatility process --study configs/study.oil-hormuz.example.yaml
```

Purpose:

- normalize raw posts;
- compute market volatility windows;
- normalize activity windows;
- generate processed CSVs.

### 4. Generate reports

```bash
python -m ostium_social_volatility report --study configs/study.oil-hormuz.example.yaml
```

Purpose:

- generate event-study report;
- generate volatility-control report;
- generate public-facing report assets or data bundles.

### 5. Run full cached pipeline

```bash
python -m ostium_social_volatility run --study configs/study.oil-hormuz.example.yaml --mode cached
```

Purpose:

- validate config;
- use existing raw/cached data;
- regenerate processed data and reports;
- validate outputs.

This should be the default low-risk reproducibility proof.

### 6. Run full live pipeline

```bash
python -m ostium_social_volatility run --study configs/study.oil-hormuz.example.yaml --mode live
```

Purpose:

- collect fresh source data;
- regenerate everything;
- validate outputs.

This requires credentials/source access and should clearly warn users before live API calls.

## Target NPM Aliases

Because SDK collection currently uses Node, package scripts can provide aliases:

```json
{
  "scripts": {
    "validate": "python -m ostium_social_volatility validate --study configs/study.oil-hormuz.example.yaml",
    "run:cached": "python -m ostium_social_volatility run --study configs/study.oil-hormuz.example.yaml --mode cached",
    "run:live": "python -m ostium_social_volatility run --study configs/study.oil-hormuz.example.yaml --mode live",
    "test": "python -m pytest -q"
  }
}
```

Keep lower-level commands for advanced users:

```json
{
  "scripts": {
    "collect:event-study-activity": "node scripts/collect_event_study_activity_windows.mjs",
    "collect:volatility-control-activity": "node scripts/collect_volatility_control_activity_windows.mjs"
  }
}
```

## Mapping Current Scripts to Target Stages

### collect stage

Current scripts:

- `scripts/collect_event_study_activity_windows.mjs --study configs/study.oil-hormuz.example.yaml`
- `scripts/collect_volatility_control_activity_windows.mjs --study configs/study.oil-hormuz.example.yaml`

Current cleanup status:

- Both scripts now accept the study config.
- Market labels, Ostium Builder symbols, pair IDs, raw X post path, market OHLC dir, and raw output paths are read from config.
- The event-study collector no longer hardcodes Chris-local project-artifact paths; the oil/Hormuz fixture is available at `data/raw/social/x_ostium_oil_90d.json` for cached/local reproducibility.

Remaining cleanup:

- Generalize older historical v1/v1.1 collectors only if they remain part of the public rerun surface.
- Add live/source-access warnings before wrapping these collectors in the high-level `run --mode live` command.

### process/report stage

Current scripts:

- `scripts/run_event_study_report.py --study configs/study.oil-hormuz.example.yaml`
- `scripts/run_volatility_control_report.py --study configs/study.oil-hormuz.example.yaml`

Current cleanup status:

- Both report scripts now consume the study config for key raw/processed/report paths and configured markets.
- v1.4 consumes config for volatility threshold and minimum baseline observations.
- `python -m ostium_social_volatility report --study ...` runs both report scripts in order.

Remaining cleanup:

- Split processing from report rendering if that becomes necessary for dashboard data bundles.
- Emit richer machine-readable summary JSON if the dashboard needs it.

### validate stage

New needed script/module:

- `src/ostium_social_volatility/validate.py`
- or `scripts/validate_pipeline.py` as a simpler interim step.

Checks:

- config schema;
- raw input availability;
- processed output contracts;
- report output existence;
- headline row counts;
- public safety scan.

## Minimal Pipeline Implementation Sequence

### Step 1 — Add config and docs

Already drafted:

- `configs/study.oil-hormuz.example.yaml`
- `docs/pipeline-cleanup-audit.md`
- `docs/data-contracts.md`
- `docs/command-surface.md`

### Step 2 — Build cached validator first

Why cached first:

- low-risk;
- uses existing files;
- verifies current analysis can be audited without live API calls;
- establishes expected counts before refactoring collectors.

First validator command:

```bash
python scripts/validate_pipeline.py --study configs/study.oil-hormuz.example.yaml --mode cached
```

Expected output:

- JSON summary with pass/fail checks.
- Non-zero exit if critical checks fail.

### Step 3 — Add config loader

Add:

- `src/ostium_social_volatility/study_config.py`

Capabilities:

- parse YAML;
- validate required keys;
- resolve repo-relative paths;
- expose market/window settings.

### Step 4 — Make reports consume config

Refactor only after validator is green.

Priority order:

1. `run_volatility_control_report.py`
2. `run_event_study_report.py`
3. Node collectors

### Step 5 — Add single entrypoint

Add later:

```bash
python -m ostium_social_volatility run --study ...
```

Only after config loader and validator exist.

## Agent-Facing Instructions

When another agent is asked to rerun or adapt the project:

1. Start with `validate --mode cached`.
2. Do not call live APIs until cached validation passes.
3. If adapting markets, update config first.
4. Discover pair IDs before collecting activity.
5. Run a small live smoke test before full live collection.
6. Generate reports.
7. Validate headline counts and caveats.
8. Avoid causal language unless a stronger design is added.

## Out of Scope for This Public Kit

Do not use this public kit to:

- create the public GitHub repo;
- deploy a Vercel dashboard;
- write the final Hermes skill;
- implement live recommendation monitoring.

Those remain separate approval-gated extensions.
