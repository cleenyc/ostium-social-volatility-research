# Data Contracts and Validation Checks

Date: 2026-05-12  
Status: Draft data contract for reproducible pipeline cleanup

## Purpose

This document defines the minimum raw and processed data contracts needed to make the Ostium Social Volatility Research Kit rerunnable by another user or agent.

The public repo should not rely on hidden assumptions in scripts. Every major input/output table should have documented required columns, row expectations, and validation checks.

## Contract 1 — Study Config

Example file:

- `configs/study.oil-hormuz.example.yaml`

Required top-level keys:

- `schema_version`
- `study`
- `social`
- `classification`
- `markets`
- `windows`
- `volatility`
- `activity`
- `paths`
- `validation`

Validation checks:

- Config parses as YAML.
- `study.id` exists and is slug-safe.
- `study.start_time < study.end_time`.
- At least one market exists.
- Each market has `label`, `ostium_builder_symbol`, and `ostium_pair_id`.
- `volatility.min_baseline_observations >= 1`.
- `activity.metrics.primary_notional_formula` is explicitly stated.

## Contract 2 — Raw X Posts JSON

Current local source:

- `local-provenance/2026-05-11-readonly-spike/raw_x_ostium_oil_90d.json`

Target public/reproducible path:

- `data/raw/social/x_ostium_oil_90d.json`

Expected shape:

```json
{
  "data": [
    {
      "id": "...",
      "text": "...",
      "created_at": "...",
      "conversation_id": "...",
      "public_metrics": { }
    }
  ]
}
```

Required post fields:

- `id`
- `text`
- `created_at`
- `public_metrics`

Optional post fields:

- `conversation_id`
- `entities`
- impressions/bookmarks if returned in current API tier.

Validation checks:

- `data` exists and is a list.
- Each post has unique `id`.
- Each post has parseable `created_at`.
- At least one post matches configured classification terms.
- For oil/Hormuz fixture, row count should be at least 29.

## Contract 3 — Normalized Posts CSV

Current equivalent:

- v1.3 event CSV contains post-level normalized fields.

Target output:

- `data/processed/posts.csv`

Required columns:

- `tweet_id`
- `url`
- `created_at`
- `date_utc`
- `post_type`
- `categories`
- `text` or `text_summary`
- `impressions`
- `engagement_count`

Validation checks:

- `tweet_id` unique.
- `date_utc` parseable.
- `post_type` in `original`, `reply`, `retweet`, `quote`, `unknown`.
- `categories` non-empty for included study posts.
- `impressions` numeric or blank.
- Oil/Hormuz fixture expected counts:
  - 29 posts.
  - 21 unique dates.
  - 20 originals.
  - 5 replies.
  - 4 retweets.

## Contract 4 — Raw Market OHLC CSV

Current files:

- `data/raw/market_ohlc/CL-USD_daily_ohlc.csv`
- `data/raw/market_ohlc/BRENT-USD_daily_ohlc.csv`

Required columns:

- `date`
- `open`
- `high`
- `low`
- `close`

Validation checks:

- `date` parseable and unique per market.
- `open`, `high`, `low`, `close` numeric.
- `high >= low`.
- `open` and `close` positive.
- Enough rows exist to compute configured baseline.
- For oil/Hormuz fixture:
  - WTI should produce at least 75 eligible days after baseline filtering.
  - Brent should produce at least 26 eligible days after baseline filtering.

## Contract 5 — Market Volatility Event Windows CSV

Current file:

- `data/processed/market_volatility_event_windows.csv`

Required columns:

- `date_utc`
- `market`
- `metric`
- `baseline30_avg`
- `event0_2_avg`
- `event0_2_lift_pct`
- `event0_2_z_score`
- `event0_2_percentile_vs_baseline`
- `context0_7_avg`
- `context0_7_lift_pct`
- `baseline_observations`
- `event_observations`
- `context_observations`

Validation checks:

- Required columns exist.
- Markets match configured market labels.
- Metrics include `range_pct` and `abs_return_pct` unless config changes.
- Baseline observations are non-negative integers.
- Primary event rows exist for every configured event date/market/metric.

## Contract 6 — Raw SDK Activity Windows JSON

Current files:

- `data/raw/event_study_activity_windows/event_study_activity_windows_summary.json`
- `data/raw/volatility_control_activity_windows/volatility_control_activity_windows_summary.json`

Expected top-level keys:

- `generatedAt`
- `methodology`
- `pairs`
- `windows`
- `errors`

Required window fields:

- `date`
- `segment`
- `start`
- `end`
- `days`
- `isPartial`
- `label`
- `pairId`
- `symbol`
- `fillCount`
- `notionalUsd`
- `openingFeesUsd`
- `totalFeesUsd`
- `actions`
- `sides`

Additional event-study window field:

- `postId`, nullable for date-level windows.

Validation checks:

- `errors` is empty or explicitly accepted by config.
- `windows` list is non-empty.
- Every configured market has windows.
- Required segments exist:
  - `baseline30`
  - `event0_2`
  - `event1_2` for event-study runs
  - `context0_7` for event-study runs
  - `post_baseline30`, `post_event48h`, `post_event72h` for post-time runs
- `notionalUsd` and `fillCount` are numeric.
- `days > 0`.

## Contract 7 — Processed Event-Study Activity Windows CSV

Current file:

- `data/processed/event_study_activity_windows.csv`

Required columns:

- `date_utc`
- `tweet_id`
- `market`
- `segment`
- `start`
- `end`
- `days`
- `is_partial`
- `fill_count`
- `fills_per_day`
- `notional_usd`
- `notional_usd_per_day`
- `opening_fees_usd`
- `opening_fees_usd_per_day`
- `total_fees_usd`

Validation checks:

- Required columns exist.
- Segments match expected segment labels.
- No negative `fill_count`.
- No negative `notional_usd`.
- Event windows exist for every post date and market.
- Post-time windows exist for every tweet ID and market.

## Contract 8 — v1.3 Event-Study CSV

Current file:

- `reports/ostium-oil-hormuz-event-study-v1_3.csv`

Minimum required post columns:

- `tweet_id`
- `url`
- `created_at`
- `date_utc`
- `post_type`
- `categories`
- `text`
- `impressions`
- `engagement_count`

Required metric families per market:

- `{MARKET}_range_*`
- `{MARKET}_abs_return_*`
- `{MARKET}_notional_*`
- `{MARKET}_fills_*`
- `{MARKET}_opening_fees_event0_2_per_day`

Oil/Hormuz fixture validation:

- 29 rows.
- 29 unique tweet IDs.
- 21 unique dates.
- WTI activity columns populated for 29 rows where applicable.
- Brent rows may be partially empty for early periods; this should be allowed but counted.

## Contract 9 — v1.4 Volatility-Control CSV

Current files:

- `reports/ostium-oil-hormuz-volatility-control-v1_4.csv`
- `data/processed/volatility_control_days.csv`

Required columns:

- `date_utc`
- `market`
- `range_pct`
- `range_baseline30_avg_pct`
- `range_lift_pct`
- `range_percentile_vs_baseline`
- `range_baseline_obs`
- `has_oil_post`
- `oil_post_count`
- `oil_original_count`
- `top_oil_post_impressions`
- `activity_baseline30_notional_per_day`
- `activity_event0_2_notional_per_day`
- `activity_event0_2_lift_pct`
- `activity_baseline30_fills_per_day`
- `activity_event0_2_fills_per_day`
- `activity_event0_2_fills_lift_pct`
- `activity_event0_2_partial`
Validation has two modes:

- **Portable validation**: structural checks only, with observed counts reported but not treated as universal constants. New studies should use this mode by omitting `validation.fixture_expectations`.
- **Fixture validation**: exact expected counts for a known reproducibility snapshot. The oil/Hormuz example uses this to lock v1.3/v1.4 artifacts to known counts.

Current oil/Hormuz fixture expectations:

- Posts: 29.
- Unique post dates: 21.
- WTI eligible rows: 75.
- Brent eligible rows: 26.
- WTI high-volatility rows: 25.
- Brent high-volatility rows: 5.
- WTI high-volatility post rows: 10.
- WTI high-volatility no-post rows: 15.
- Brent high-volatility post rows: 1.
- Brent high-volatility no-post rows: 4.

Portable configs should not copy these counts unless intentionally creating a new fixture snapshot. Market-specific expected counts should be declared generically by market label under `validation.fixture_expectations.markets`, not with hardcoded WTI/Brent validator logic.

## Public Safety Validation

Before public export or GitHub publication, validate that output/public paths do not include:

- `.env`
- local X auth config
- `google_token.json`
- `google_client_secret.json`
- local Hermes config
- private API keys
- raw secret-bearing logs

The report/dashboard can feature tweet URLs. Full raw X JSON and tweet text/metrics should be reviewed before committing to a public repo.

## Suggested Validator Output

A future validator should print a compact result like:

```json
{
  "ok": true,
  "study": "oil_hormuz",
  "checks": {
    "config": "ok",
    "raw_x_posts": "ok",
    "market_ohlc": "ok",
    "sdk_activity_windows": "ok",
    "event_study_csv": "ok",
    "volatility_control_csv": "ok",
    "public_safety": "ok"
  },
  "counts": {
    "posts": 29,
    "unique_post_dates": 21,
    "wti_eligible_days": 75,
    "wti_high_vol_days": 25,
    "brent_eligible_days": 26,
    "brent_high_vol_days": 5
  }
}
```
