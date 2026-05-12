# Ostium Social Volatility Study — Methodology and Reproducibility Appendix

Date: 2026-05-12  
Status: Phase 1 draft appendix for public research package

## Purpose

This appendix documents how the oil/Hormuz study was sourced, processed, and interpreted, and how an internal Ostium/Hermes user could rerun or modify the analysis.

The goal is to make the project reproducible without exposing local credentials, private auth files, or environment-specific state.

## Required Access

### 1. X / Twitter access

The original study used X full-archive search to collect historical `@Ostium` posts.

Supported collection paths for the public research kit should include both:

1. `xurl`-based collection.
2. Raw X API collection.

Required X capabilities:

- historical/full-archive search, not only recent search;
- tweet fields including `created_at`, `text`, `public_metrics`, and ideally impressions/bookmarks if the authenticated tier exposes them;
- ability to query official `@Ostium` posts by account and keyword.

Important note:

- `xurl search` may hit recent-search semantics only.
- For historical analysis, use the raw X API full-archive endpoint where available:

```text
/2/tweets/search/all
```

Example conceptual query:

```text
from:Ostium oil
```

For modified studies, replace the search terms:

- copper: `from:Ostium copper OR HG`
- gold: `from:Ostium gold OR XAU`
- silver: `from:Ostium silver OR XAG`
- indices: `from:Ostium SPX OR US500 OR NDX OR US100`
- FX: `from:Ostium USDJPY OR "USD/JPY" OR EURUSD OR "EUR/USD"`

Final query syntax should be validated against X API rules and available tier limits.

### 2. Ostium Builder API

The study used Ostium Builder API OHLC data for market volatility.

Relevant market symbols verified during feasibility:

- `CL-USD` — crude oil / WTI proxy.
- `BRENT-USD` — Brent.
- `HG-USD` — copper.
- `XAU-USD` — gold.
- `XAG-USD` — silver.
- `SPX-USD` — S&P 500 proxy.
- `NDX-USD` — Nasdaq proxy.
- `BTC-USD`, `ETH-USD`.
- FX pairs such as `USD-JPY`, `EUR-USD`, `GBP-USD`.

Rule:

> Use Ostium's own pair symbols from its live prices/pairs endpoint. Do not assume external ticker names.

### 3. Ostium SDK / Builder SDK

The study used read-only SDK access to collect all-user per-market fills.

Core method shape:

```text
OstiumClient.createReadOnly()
getFillsByTime({ user: 'ALL', pairId, startTime, endTime })
```

Pair IDs used in the oil/Hormuz study:

- WTI / CL pairId: `7`
- Brent pairId: `55`

For another market, the rerun process must identify the relevant pair ID before collecting activity windows.

The activity metric used in the study is:

```text
estimated_notional_usd = abs(px * szi)
```

This was selected because SDK source/types indicate:

- `Fill.px` is execution price;
- `Fill.szi` is trade size in base-asset units;
- SDK formatting maps subgraph `tradeNotional` to `szi`.

### 4. Optional aggregate protocol proxies

Early feasibility used DefiLlama aggregate protocol metrics:

- TVL;
- fees/revenue;
- open interest.

These are useful for feasibility and context, but not market-specific enough for the final headline conclusion. Use per-market SDK fills for the main activity outcome whenever possible.

## Study Configuration

A future configurable repo should expose a study config similar to:

```yaml
study:
  name: oil_hormuz
  account: Ostium
  x_query: 'from:Ostium oil'
  start_time: '2026-02-10T00:00:00Z'
  end_time: '2026-05-11T23:59:59Z'

markets:
  - label: WTI
    builder_symbol: CL-USD
    ostium_pair_id: 7
  - label: BRENT
    builder_symbol: BRENT-USD
    ostium_pair_id: 55

classification:
  include_terms:
    - oil
    - crude
    - brent
    - wti
    - hormuz
    - CL
  categories:
    hormuz: ['hormuz', 'strait']
    brent: ['brent']
    wti_cl: ['wti', 'CL']
    crude: ['crude']

event_windows:
  primary_calendar: '0-2d'
  robustness_post_time:
    - '+48h'
    - '+72h'
  robustness_calendar: '1-2d'
  context_calendar: '0-7d'

baselines:
  activity_days: 30
  volatility_days: 30
  min_market_baseline_observations: 10

volatility_control:
  high_volatility:
    range_lift_pct_gt: 0
    range_percentile_gte: 75
```

For copper, a user would change at minimum:

```yaml
study:
  name: copper
  x_query: 'from:Ostium copper OR HG'

markets:
  - label: COPPER
    builder_symbol: HG-USD
    ostium_pair_id: <lookup_required>

classification:
  include_terms:
    - copper
    - HG
```

The agent/runbook should instruct the user or agent to discover and confirm the pair ID before running activity collection.

## Pipeline Steps

### Step 1 — Collect social posts

Inputs:

- X account: `Ostium`.
- Query terms.
- Start/end window.

Outputs:

- raw X response JSON;
- normalized posts CSV.

Normalized fields should include:

- `tweet_id`
- `url`
- `created_at`
- `date_utc`
- `post_type`
- `categories`
- `text` or public-safe summary
- `impressions`
- `engagement_count`

### Step 2 — Classify posts

Classify each post by:

- post type: original, reply, retweet;
- market/topic categories: oil, WTI, Brent, Hormuz, crude, etc.;
- whether the post belongs in the selected study corpus.

For public reports, keep tweet URLs visible and consider whether full text should be included.

### Step 3 — Collect market OHLC

For each configured market:

- fetch daily OHLC from Ostium Builder API;
- compute daily range percentage;
- compute absolute open-to-close return;
- compute rolling 30-day baseline metrics;
- compute range lift and percentile versus baseline.

Core metrics:

- `range_pct`
- `range_baseline30_avg_pct`
- `range_lift_pct`
- `range_percentile_vs_baseline`
- `range_baseline_obs`

### Step 4 — Collect activity windows

For each event/post date and each configured market:

- collect 30-day pre-event baseline activity;
- collect calendar 0–2d event activity;
- collect exact post-time +48h and +72h windows;
- optionally collect 1–2d and 0–7d context windows.

Core metrics:

- notional/day;
- fills/day;
- notional lift vs baseline;
- fills lift vs baseline;
- opening fees/day where available.

### Step 5 — Generate event study

Create one row per post.

Include:

- social metrics;
- WTI/Brent market volatility windows;
- WTI/Brent activity windows;
- exact post-time robustness metrics;
- caveats for partial windows.

This corresponds to the v1.3 event-study layer.

### Step 6 — Generate volatility-day control

Create one row per market/day.

Include:

- market volatility metrics;
- whether that date had an oil/topic post;
- post counts;
- original post counts;
- top post impressions;
- activity window metrics.

Filter high-volatility days using the configured threshold, then compare post vs no-post days.

This corresponds to the v1.4 control layer.

### Step 7 — Generate reports

Generate:

- event-study report;
- volatility-control report;
- public narrative report;
- dashboard data bundle.

## Interpretation Rules

### Use causal language carefully

Allowed:

- “aligned with”
- “coincided with”
- “directional evidence”
- “positive correlation”
- “may have amplified”

Avoid:

- “caused”
- “proved”
- “drove” unless supported by a stronger design
- “ROI” unless there is a defined economic model

### Separate social reach from activity

Do not assume a high-impression post means activity lifted. Treat social reach, market volatility, and trading activity as separate outcomes.

### Separate WTI from Brent

Do not generalize WTI conclusions to Brent without checking Brent sample size and launch/ramp effects.

### Do not overcount duplicated windows

If multiple posts share a date, post-level rows may share the same calendar activity window. Use clustered/date-level views for headline conclusions.

## Reproducibility Commands From Current Local Repo

Current local commands used in the internal repo:

```bash
# Collect v1.3 event-study activity windows
node scripts/collect_event_study_activity_windows.mjs

# Generate v1.3 event-study report
python3 scripts/run_event_study_report.py

# Collect v1.4 volatility-control activity windows
node scripts/collect_volatility_control_activity_windows.mjs

# Generate v1.4 volatility-control report
python3 scripts/run_volatility_control_report.py

# Run tests
python3 -m pytest -q
```

In the public repo, replace environment-specific Python interpreter with a portable command such as:

```bash
python -m pytest -q
python scripts/run_event_study_report.py
python scripts/run_volatility_control_report.py
```

## Public Repo Safety Checklist

Before publishing:

- [ ] No `.env` files.
- [ ] No X/Twitter auth files.
- [ ] No local `xurl` auth config.
- [ ] No Hermes config/secrets.
- [ ] No private API keys.
- [ ] No local-only absolute paths in public README commands.
- [ ] Tweet links are acceptable for public presentation.
- [ ] Full tweet text/metrics reviewed before publishing raw CSVs.
- [ ] Example config uses placeholders for credentials and pair IDs.
- [ ] Public report uses correlational language.

## Agent Instructions for Rerunning / Modifying the Study

A Hermes agent or other coding agent should follow this pattern:

1. Read the study config.
2. Confirm required credentials are available without printing secrets.
3. Verify X full-archive access or ask the user to provide it.
4. Verify Ostium Builder API market symbol exists.
5. Discover and confirm Ostium pair ID for the selected market.
6. Run a small smoke test for social posts, OHLC, and activity fills.
7. Generate cached raw data.
8. Normalize processed tables.
9. Generate event-study report.
10. Generate volatility-day control report.
11. Generate public narrative summary.
12. State caveats and unsupported claims.

If adapting oil to copper, the agent should not merely replace words. It must re-run:

- X query discovery;
- market symbol validation;
- pair ID discovery;
- activity collection;
- event-study generation;
- volatility-control comparison;
- final interpretation.
