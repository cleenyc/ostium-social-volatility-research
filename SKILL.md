---
name: ostium-social-volatility-research-kit
description: Use when running, modifying, or interpreting the Ostium Social Volatility Research Kit, a configurable event-study and volatility-control workflow that compares market-specific social posts, oil-market volatility, and Ostium trading activity.
version: 0.1.0
author: Chris Lee
metadata:
  hermes:
    tags: [ostium, research, event-study, dashboard, social-volatility]
    related_skills: []
---

# Ostium Social Volatility Research Kit

## Overview

This skill makes the repo agent-runnable. It guides a Hermes Agent or similar coding agent through reproducing the cached oil/Hormuz study, regenerating the dashboard, adapting the study config to another market/topic, and interpreting the results without drifting into unsupported causal or live-monitoring claims.

The canonical scope guard for this repo is:

- **Static dashboard:** local/static dashboard, report sections, charts/tables, post/market drilldowns, configurable cached controls, downloadable outputs. No deployment unless explicitly approved later.
- **Agent runbook and prompt templates:** this skill, runbook, prompt templates, install/use instructions, and adaptation guide. No deployment, recurring jobs, or live recommendation engine without separate approval.

## When to Use

Use this skill when the user asks to:

- reproduce the oil/Hormuz research kit locally;
- validate cached study artifacts;
- regenerate the v1.3 event-study report, v1.4 volatility-control report, or static dashboard;
- adapt the study from oil/Hormuz to another market/topic;
- explain required data/API access for a new run;
- interpret dashboard/report outputs and caveats;
- review or update public packaging without deploying or enabling live jobs.

Do **not** use this skill to deploy a dashboard, push/publish remote changes, create live monitoring jobs, modify credentials, send external messages, or build a recommendation engine without explicit approval. Those are separate approval-gated actions.

## Quick Start

From the repo root:

```bash
npm install
npm run run:cached
npm run dashboard:data
npm run test
python3 -m http.server 8765 --directory dashboard
```

Open the dashboard locally at:

```text
http://127.0.0.1:8765/
```

If `python3` is not available in your environment, replace it with a Python interpreter that has the repo test dependencies installed.

## Canonical Commands

```bash
# Validate cached artifacts
PYTHONPATH=src python3 -m ostium_social_volatility validate --study configs/study.oil-hormuz.example.yaml

# Regenerate cached v1.3/v1.4 reports
PYTHONPATH=src python3 -m ostium_social_volatility report --study configs/study.oil-hormuz.example.yaml

# Regenerate reports and validate in one command
PYTHONPATH=src python3 -m ostium_social_volatility run --study configs/study.oil-hormuz.example.yaml --mode cached

# Build dashboard bundle and downloadable static artifacts
PYTHONPATH=src python3 scripts/build_dashboard_data.py --study configs/study.oil-hormuz.example.yaml --out-dir dashboard/data

# Run tests
PYTHONPATH=src python3 -m pytest -q
```

NPM aliases are also available:

```bash
npm run validate
npm run report
npm run run:cached
npm run dashboard:data
npm run test
```

## Inputs Needed

For the cached oil/Hormuz fixture, no new external credentials are required. The repo uses already-cached local artifacts.

For a new or live collection run, the agent must identify or obtain:

- X/Twitter full-archive search access, either through `xurl` or raw X API;
- Ostium Builder API / SDK access for OHLC and pair-specific fills;
- market symbols, Ostium pair IDs, and topic/query terms;
- a safe raw-data storage path under `data/raw/`;
- a reviewed public-output policy for tweet text, tweet URLs, and any metrics with redistribution concerns.

Never commit credentials, token files, `.env`, `.xurl`, OAuth files, auth directories, or secret-bearing logs.

## Study Config Adaptation

Start by copying the example config:

```bash
cp configs/study.oil-hormuz.example.yaml configs/study.<topic>.example.yaml
```

Change at minimum:

- `study.id`, `study.title`, `study.description`, date range;
- `social.x.query` and topic include terms;
- `classification.include_terms` and category mapping;
- `markets[].label`, `ostium_builder_symbol`, `ostium_pair_id`, and display names;
- `paths.*` so outputs do not overwrite the oil/Hormuz fixture;
- `validation.fixture_expectations` after the first baseline run, or remove them for exploratory runs.

Keep the primary decision window as `0-2d` unless the user explicitly changes methodology. Treat `+48h` and `+72h` as robustness views, not replacements for the headline metric.

## Interpretation Rules

- Headline claim: WTI oil/Hormuz results are directional/correlational, not causal.
- Brent is underpowered in the cached study and should not be overclaimed.
- Distinguish social reach, market volatility, and trading activity; they are related but not interchangeable.
- Treat retweets/replies/originals separately when making claims.
- Same-day or adjacent posts can share activity windows; do not imply independent samples without clustering.
- Dashboard controls recalculate cached views; they do not create new source data.

## Common Pitfalls

1. **Using live mode prematurely.** `run --mode live` is intentionally disabled until source warnings and credential behavior are explicit.
2. **Publishing local artifacts by accident.** Repo-local skill/runbook artifacts are safe to update, but publication/deployment still needs explicit approval.
3. **Overclaiming causality.** The study is observational and correlational.
4. **Overwriting the oil fixture.** Adapted studies should write to new config/output paths.
5. **Ignoring public-data review.** Tweet text and raw X artifacts should be reviewed before public packaging.
6. **Treating the dashboard as deployed.** The current dashboard is local/static only.

## Verification Checklist

- [ ] `npm run run:cached` passes with validation success.
- [ ] `npm run dashboard:data` rebuilds `dashboard/data/summary.json`.
- [ ] `npm run test` passes.
- [ ] Local dashboard renders report sections, WTI/Brent summaries, market-day explorer, post drilldown, and download links.
- [ ] Adapted configs do not overwrite the oil/Hormuz fixture unless explicitly intended.
- [ ] No credentials or private auth files are present in commits or public artifacts.
- [ ] Claims remain correlational and caveated.
