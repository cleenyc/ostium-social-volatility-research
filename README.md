# Ostium Social Volatility Research Kit

A reproducible research kit for testing whether market-specific Ostium social posts coincide with market volatility and Ostium protocol activity.

The included reference study analyzes Ostium oil/Hormuz posts against WTI and Brent volatility and per-market Ostium activity. The kit is designed to be cloned, inspected, rerun from cached fixtures, and adapted to a new market/topic with config changes instead of code rewrites.

## What is included

- **Research report package**: public-facing narrative, methodology appendix, figure/table spec, and source/synthesis report in `reports/`.
- **Reproducible cached pipeline**: config-first Python CLI and tests for regenerating the oil/Hormuz outputs from committed fixture data.
- **Static dashboard prototype**: local `dashboard/` with embedded report sections, WTI/Brent summaries, market-day explorer, post drilldown, and download links.
- **Agent runbook / Hermes skill**: `SKILL.md`, `docs/agent-runbook.md`, `docs/adapt-study.md`, and prompt templates in `prompts/`.
- **Public-safe fixture snapshot**: cached X/OHLC/Ostium activity artifacts needed for the reference rerun. No credentials are committed.

## Project status

This repository is a public-facing, static research kit: the report package, cached reproduction pipeline, local dashboard, and agent runbook are included. Live monitoring, recommendation engines, recurring jobs, and credentialed collectors are intentionally out of scope unless reviewed separately.

## Quick start: reproduce the cached oil/Hormuz study

Prerequisites:

- Python 3.11+
- Node.js 20+ recommended
- npm

Install dependencies:

```bash
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -e '.[dev]'
npm install
```

Run the cached pipeline:

```bash
PYTHONPATH=src python3 -m ostium_social_volatility run \
  --study configs/study.oil-hormuz.example.yaml \
  --mode cached
```

Equivalent npm wrapper:

```bash
npm run run:cached
```

Expected cached validation summary:

- v1.3 event study: 29 posts, 21 unique dates, 84 market windows, 342 activity windows.
- v1.4 volatility control: 101 rows, 30 high-volatility rows.
- Validation: no failures for the committed reference fixture.

Run tests:

```bash
npm run test
```

## View the dashboard locally

```bash
npm run dashboard:data
python3 -m http.server 8765 --directory dashboard
```

Open `http://127.0.0.1:8765/`.

This is a static/local dashboard. Public hosting is optional and can be done with GitHub Pages, Vercel, Cloudflare Pages, or any static host by serving `dashboard/` after regenerating `dashboard/data/summary.json`.

## Adapt the study to another market/topic

Start from `configs/study.oil-hormuz.example.yaml` and change:

- `study.id`, title, time window, and description;
- X query terms and classification terms;
- Ostium market labels, symbols, and pair IDs;
- OHLC source files;
- volatility thresholds and event windows;
- output paths and fixture expectations.

Then follow `docs/adapt-study.md` and `prompts/adapt-study.md`.

## Live collection status

The committed reference pipeline is cached/reproducible. Lower-level collector scripts document how the fixture was produced, but high-level `run --mode live` is intentionally disabled until source-access warnings, credentials behavior, and rate-limit expectations are explicit for the user's environment.

Users who adapt the kit should bring their own X/Twitter access or `xurl` equivalent and their own Ostium SDK/source access. Do not commit credential files, token files, `.env`, `.xurl`, OAuth files, or secret-bearing logs.

## Data and publication notes

- The public-facing narrative should link to public X posts instead of embedding private auth artifacts.
- The fixture includes public social-post fields and public/on-chain or public-market-derived activity/volatility artifacts for reproducibility.
- See `docs/publication-checklist.md` before publishing or deploying a fork.
- See `docs/reproducibility.md` for the exact cached command surface and source assumptions.

## Repository map

- `configs/` — study configuration examples.
- `data/raw/` — cached source fixtures for the reference run.
- `data/processed/` — generated normalized CSVs.
- `dashboard/` — static dashboard prototype and data bundle.
- `docs/` — runbooks, data contracts, source docs, publication checks.
- `prompts/` — agent prompts for reproduction, adaptation, and interpretation.
- `reports/` — research reports and generated result tables.
- `scripts/` — wrappers, collectors, and historical/provenance scripts.
- `src/ostium_social_volatility/` — Python package and CLI.
- `tests/` — regression and packaging checks.

Author: Chris Lee.

