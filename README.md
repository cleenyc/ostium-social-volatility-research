# Ostium Social Volatility Research

This repository documents a reproducible event study testing whether Ostium oil/Hormuz-related social content drove higher Ostium platform activity during periods of elevated market volatility.

The reference study follows `@Ostium` oil/Hormuz posts across WTI and Brent markets, then compares post days with comparable volatility days that had no oil-related Ostium post. The main result is directional and correlational: for WTI, high-volatility days with oil-related Ostium posts had materially higher median activity and notional than high-volatility days without oil-related posts.

## Main finding

The strongest evidence comes from the v1.4 volatility-day control comparison:

- **WTI high-volatility post days**: 10 days.
- **WTI high-volatility no-post days**: 15 days.
- **Median activity lift with oil post**: +74.0%.
- **Median activity lift without oil post**: -9.3%.
- **Median event notional/day with oil post**: $35.9M.
- **Median event notional/day without oil post**: $6.5M.

Interpretation: the WTI evidence supports a positive directional relationship between oil/Hormuz posting, oil-market volatility, and Ostium WTI activity.

## Research question

The original research question was:

> Around a defined oil/Hormuz volatility window, did Ostium post oil-related content, how did those posts perform versus baseline, and did Ostium volume/activity shift around those posts?

As the study matured, the question became more precise:

1. Did `@Ostium` post oil/Hormuz-related content during relevant oil-volatility windows?
2. Did those posts perform well socially?
3. Were WTI or Brent volatility measures elevated around those posts?
4. Did Ostium WTI/Brent activity rise around those posts?
5. Compared with similar high-volatility days without posts, were post days associated with higher activity?

The final answer relies most heavily on the fifth question because it adds the missing control group.

## Read this first

The most important research artifacts are:

- **Research report v1**: `reports/ostium-social-volatility-research-report-v1.md`  
  The main synthesis report. Start here for the conclusion, methodology evolution, supported claims, caveats, and source inventory.

- **v1.3 event study**: `reports/ostium-oil-hormuz-event-study-v1_3.md`  
  Post-level event study across 29 oil/Hormuz posts with calendar `0-2d` windows plus exact post-time `+48h` and `+72h` robustness checks.

- **v1.4 volatility-day control**: `reports/ostium-oil-hormuz-volatility-control-v1_4.md`  
  Control comparison of high-volatility WTI/Brent days with oil posts versus high-volatility days without oil posts.

- **Reproducibility guide**: `docs/reproducibility.md`  
  Cached rerun commands, expected outputs, and source assumptions.

- **Study config**: `configs/study.oil-hormuz.example.yaml`  
  Canonical configurable inputs for the reference oil/Hormuz rerun.

## Methodology evolution

The study was intentionally iterative. Each version addressed a limitation discovered in the prior pass.

- **Feasibility / read-only spike**: verified that X full-archive search, Ostium Builder API OHLC data, and Ostium SDK read-only activity data could be joined for an oil/Hormuz study.
- **v1**: tested two hand-picked cases using SDK-derived WTI/Brent activity.
- **v1.1**: expanded from selected cases to all 29 oil-related `@Ostium` posts found in the 90-day query.
- **v1.2**: converted the work into a standardized event-study frame with a 30-day baseline and calendar `0-2d` primary window.
- **v1.3**: added exact post-time `+48h` and `+72h` robustness checks. This showed strong WTI cases, but also mixed medians and duplicate-window concerns.
- **v1.4**: added the key control comparison: high-volatility market days with oil posts versus high-volatility market days without oil posts. This produced the strongest WTI inference.

## Conclusion hierarchy

The current evidence supports these claims, in order of strength:

1. **Main conclusion — WTI**  
   WTI shows positive directional/correlational evidence: high-volatility WTI days with oil-related Ostium posts had materially higher median activity and notional than high-volatility WTI days without oil-related posts.

2. **Secondary conclusion — Brent**  
   Brent is underpowered and noisy. The study should not claim a robust Brent posting/activity relationship yet.

3. **Social reach caveat**  
   Social reach does not cleanly predict trading activity. The highest-impression post in the corpus did not coincide with a positive WTI activity lift.

4. **Causality caveat**  
   The study is observational. It supports alignment and directional correlation, not causal proof.

5. **Reusable research kit**  
   The repository packages the research as a reproducible, configurable research kit that can be rerun from cached fixtures and adapted to other markets/topics.

## What is included

- **Research report package**: canonical synthesis report, figure/table spec, event-study report, control-comparison report, and historical iteration artifacts in `reports/`.
- **Reproducible cached pipeline**: config-first Python CLI and tests for regenerating the oil/Hormuz outputs from committed fixture data.
- **Static dashboard prototype**: local `dashboard/` with embedded report sections, WTI/Brent summaries, market-day explorer, post drilldown, and download links.
- **Runbooks and prompt templates**: `SKILL.md`, `docs/agent-runbook.md`, `docs/adapt-study.md`, and prompt templates in `prompts/` for reproducing or adapting the study with Hermes or another capable coding assistant.
- **Public-safe fixture snapshot**: cached X/OHLC/Ostium activity artifacts needed for the reference rerun. No credentials are committed.

## Project status

This repository is a public-facing, static research package. It includes the report package, cached reproduction pipeline, local dashboard, and adaptation runbooks.

Live monitoring, recommendation engines, recurring jobs, and credentialed high-level collectors are intentionally out of scope unless reviewed separately.

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

Users who adapt the package should bring their own X/Twitter access or `xurl` equivalent and their own Ostium SDK/source access. Do not commit credential files, token files, `.env`, `.xurl`, OAuth files, or secret-bearing logs.

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
- `prompts/` — prompts for reproduction, adaptation, and interpretation.
- `reports/` — research reports and generated result tables.
- `scripts/` — wrappers, collectors, and historical/provenance scripts.
- `src/ostium_social_volatility/` — Python package and CLI.
- `tests/` — regression and packaging checks.

Author: Chris Lee.
