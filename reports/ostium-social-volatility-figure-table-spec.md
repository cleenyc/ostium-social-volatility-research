# Ostium Social Volatility Study — Figure and Table Specification

Date: 2026-05-12  
Status: Phase 1 draft spec for report/dashboard reuse

## Purpose

This document defines the initial visual assets and tables needed to turn the oil/Hormuz research report into a dashboard-ready public research package.

It does not build the dashboard yet. It specifies what the dashboard/report should show and which source files power each visual.

## Source Data

Primary source files:

- `reports/ostium-oil-hormuz-event-study-v1_3.csv`
- `reports/ostium-oil-hormuz-volatility-control-v1_4.csv`
- `reports/ostium-oil-hormuz-event-study-v1_3.md`
- `reports/ostium-oil-hormuz-volatility-control-v1_4.md`

## Core Report Figures

### Figure 1 — Project Timeline: v0 → v1.4

**Purpose:** Show how the project matured from a feasibility spike into a controlled comparison.

**Type:** Horizontal timeline / stepper.

**Stages:**

1. Feasibility / read-only spike
   - X full-archive query works.
   - Ostium Builder OHLC works.
   - DefiLlama aggregate proxies work.
2. v1 — two hand-picked events
   - Apr 13 social case.
   - Mar 9–10 activity case.
3. v1.1 — all 29 posts
   - Full oil corpus.
   - Post type and category tagging.
4. v1.2 — event study
   - 30-day baseline.
   - 0–2d primary window.
5. v1.3 — post-time robustness
   - +48h and +72h exact timestamp windows.
6. v1.4 — volatility-day control
   - High-volatility post vs no-post comparison.

**Dashboard interaction:** Clicking a stage opens the methodology detail for that version.

## Core Result Figures

### Figure 2 — WTI High-Volatility Post vs No-Post Activity Lift

**Purpose:** Headline result.

**Type:** Bar chart or paired summary cards.

**Data:** `reports/ostium-oil-hormuz-volatility-control-v1_4.csv`

**Filters:**

- `market == WTI`
- high-volatility definition:
  - `range_lift_pct > 0`
  - `range_percentile_vs_baseline >= 75`

**Metrics:**

- Median `activity_event0_2_lift_pct` by `has_oil_post`.
- Mean `activity_event0_2_lift_pct` by `has_oil_post`.
- Count of days by `has_oil_post`.

**Expected values:**

- With post: 10 days; median activity lift +74.0%.
- Without post: 15 days; median activity lift -9.3%.

**Interpretive caption:**

> On high-volatility WTI days, days with oil-related Ostium posts had materially higher median activity lift than high-volatility days without oil posts.

### Figure 3 — WTI High-Volatility Post vs No-Post Notional

**Purpose:** Make the economic magnitude obvious.

**Type:** Bar chart / summary cards.

**Data:** `reports/ostium-oil-hormuz-volatility-control-v1_4.csv`

**Metric:** Median `activity_event0_2_notional_per_day` by `has_oil_post` for high-volatility WTI days.

**Expected values:**

- With post: $35.9M median event notional/day.
- Without post: $6.5M median event notional/day.

**Caption:**

> High-volatility WTI post days had roughly 5.5x the median event notional/day of high-volatility WTI no-post days.

### Figure 4 — WTI Range Lift vs Activity Lift Scatter

**Purpose:** Show the relationship between market volatility and Ostium activity.

**Type:** Scatter plot.

**Data:** `reports/ostium-oil-hormuz-volatility-control-v1_4.csv`

**Filters:**

- `market == WTI`

**X-axis:** `range_lift_pct`  
**Y-axis:** `activity_event0_2_lift_pct`  
**Color:** `has_oil_post`  
**Optional shape/size:** `oil_post_count`

**Expected correlation:**

- Across eligible WTI days: 0.46.
- Across high-volatility WTI days: 0.33.

**Caption:**

> WTI activity lift was positively correlated with WTI range lift. Oil-post days cluster among several of the stronger activity outcomes, but causality is not implied.

### Figure 5 — Top WTI Event-Study Cases

**Purpose:** Connect the control result back to individual posts.

**Type:** Ranked bar chart or table.

**Data:** `reports/ostium-oil-hormuz-event-study-v1_3.csv`

**Rows:** Top original/post rows by `WTI_notional_event0_2_lift_pct`, excluding empty values.

**Columns:**

- date
- post type
- tweet URL
- impressions
- WTI range lift
- WTI 0–2d notional/day
- WTI activity lift
- post +48h activity lift

**Recommended display:** Interactive table in dashboard; top 5 in report.

### Figure 6 — Social Reach vs WTI Activity Lift

**Purpose:** Show that impressions do not equal activity.

**Type:** Scatter plot.

**Data:** `reports/ostium-oil-hormuz-event-study-v1_3.csv`

**X-axis:** `impressions` using log scale.  
**Y-axis:** `WTI_notional_event0_2_lift_pct`.  
**Color:** `post_type`.  
**Label outliers:** May 6, Mar 3, Mar 9, Mar 23.

**Caption:**

> The largest social reach outlier did not correspond to positive WTI activity lift, so impressions and market activity should be treated as separate outcomes.

### Figure 7 — Brent High-Volatility Sample Size Warning

**Purpose:** Prevent Brent overclaiming.

**Type:** Small multiples / sample-count cards.

**Data:** `reports/ostium-oil-hormuz-volatility-control-v1_4.csv`

**Expected values:**

- Brent eligible days: 26.
- Brent high-volatility days: 5.
- Brent high-volatility days with oil post: 1.
- Brent high-volatility days without oil post: 4.

**Caption:**

> Brent is directionally interesting but underpowered. Only one high-volatility Brent post day exists in the current control sample.

## Core Tables

### Table 1 — Study Coverage

**Source:** v1.3 and v1.4 reports/CSVs.

Rows:

- Oil posts: 29.
- Unique post dates: 21.
- Original posts: 20.
- Replies: 5.
- Retweets: 4.
- WTI eligible days: 75.
- WTI high-volatility days: 25.
- Brent eligible days: 26.
- Brent high-volatility days: 5.

### Table 2 — WTI Control Summary

Columns:

- group: high-vol post days / high-vol no-post days
- days
- median activity lift
- mean activity lift
- positive activity days
- median event notional/day

Expected rows:

- With oil post: 10; +74.0%; +402.2%; 5/10; $35.9M.
- Without oil post: 15; -9.3%; +105.0%; 6/15; $6.5M.

### Table 3 — Brent Control Summary

Columns:

- group
- days
- median activity lift
- mean activity lift
- positive activity days
- median event notional/day

Expected rows:

- With oil post: 1; -75.1%; -75.1%; 0/1; $1.4M.
- Without oil post: 4; -98.6%; -94.3%; 0/4; $222k.

### Table 4 — Top Social Reach Posts

Source: `reports/ostium-oil-hormuz-event-study-v1_3.csv`.

Columns:

- date
- post type
- impressions
- WTI range lift
- WTI activity lift
- URL
- short post text

### Table 5 — Top Activity Posts

Source: `reports/ostium-oil-hormuz-event-study-v1_3.csv`.

Columns:

- date
- post type
- impressions
- WTI 0–2d notional/day
- WTI 0–2d activity lift
- WTI post +48h activity lift
- URL

## Dashboard Sections

### Section 1 — Report

Render the public research report as the first/default tab.

### Section 2 — Headline Result

Show WTI post vs no-post comparison with Figure 2 and Figure 3.

### Section 3 — Event Explorer

Interactive table over v1.3 post-level rows.

Filters:

- market: WTI / Brent
- post type: original / reply / retweet
- category: oil / WTI / Brent / Hormuz / crude
- date range
- minimum impressions
- positive/negative activity lift

### Section 4 — Volatility Control Explorer

Interactive market-day table over v1.4 rows.

Filters:

- market
- high-volatility only
- post days only
- no-post days only
- min/max range lift
- min/max activity lift

### Section 5 — Methodology and Reproducibility

Human-readable pipeline documentation and agent runbook links.

## Public-Safety Notes

- Display tweet URLs rather than embedding private local raw X responses.
- Never expose auth files, tokens, `.env`, local xurl config, or Hermes config.
- If publishing CSVs, review whether tweet text and impression fields are acceptable for public distribution. Chris's current stance is that public presentation via tweet links is acceptable.
- Prefer reproducible commands plus sample/sanitized fixtures if there is any uncertainty.
