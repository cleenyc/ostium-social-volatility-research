# Ostium Social Volatility Study: Oil/Hormuz Posting, Market Volatility, and Trading Activity

**Draft:** Public-facing research report  
**Date:** 2026-05-12  
**Scope:** Oil/Hormuz analysis through v1.4  
**Status:** Draft for review; not yet final/public-published

## Executive Summary

This study asks whether Ostium's oil-related social posts coincided with periods of elevated oil-market volatility and increased Ostium trading activity.

The short answer is: **yes, directionally for WTI; not conclusively for Brent.**

Across the completed oil/Hormuz analysis, the strongest evidence comes from the v1.4 volatility-day control comparison. On high-volatility WTI days, days where Ostium posted oil-related content had materially higher Ostium WTI activity than comparable high-volatility days without oil posts.

Key WTI result:

- High-volatility WTI days with oil posts: **10**
- High-volatility WTI days without oil posts: **15**
- Median WTI activity lift with oil posts: **+74.0%**
- Median WTI activity lift without oil posts: **-9.3%**
- Median event notional/day with oil posts: **$35.9M**
- Median event notional/day without oil posts: **$6.5M**

This does **not** prove that posting caused trading activity. The safer conclusion is that Ostium's oil/Hormuz posting aligned with periods of elevated WTI volatility and higher WTI activity, and may have amplified attention or participation during those windows.

Brent remains underpowered. The Brent control sample contains only five high-volatility Brent days, and only one of them had an oil-related Ostium post. That is not enough to support the same conclusion.

## The Original Question

The project began with a practical growth/research question:

> During a defined oil/Hormuz volatility window, did Ostium post oil-related content, how did those posts perform versus baseline, and did Ostium volume/activity shift around those posts?

That question became a structured study with five parts:

1. Did Ostium post oil/Hormuz-related content during the study period?
2. Were those posts socially meaningful relative to other Ostium posts?
3. Was WTI or Brent volatility elevated around those posts?
4. Did Ostium WTI/Brent trading activity shift around those posts?
5. On high-volatility oil-market days, did post days differ from no-post days?

The fifth question is the most important addition. Early analysis could show that posts and activity moved together. The v1.4 control comparison added a more useful benchmark: high-volatility days where Ostium did **not** post oil content.

## Study Design at a Glance

The final version combines three datasets:

1. **Ostium social posts**
   - Official `@Ostium` X/Twitter posts.
   - Query focus: oil/Hormuz content.
   - Final corpus: **29 posts across 21 dates**.

2. **Oil market volatility**
   - WTI proxy: `CL-USD` daily OHLC from Ostium Builder API.
   - Brent: `BRENT-USD` daily OHLC from Ostium Builder API.
   - Volatility metric: daily intraday range versus a rolling 30-day baseline.

3. **Ostium market-specific activity**
   - WTI pairId: `7`.
   - Brent pairId: `55`.
   - Source: read-only Ostium SDK fills.
   - Primary activity metric: estimated USD execution notional/day from fill rows.

The primary event window is **0–2 days**: the post date through two calendar days after. The primary baseline is the prior **30 calendar days**, end-exclusive.

## The Dataset

The post corpus contains:

- **29** oil/Hormuz-related posts.
- **21** unique dates.
- **20** original posts.
- **5** replies.
- **4** retweets.
- **3,744,063** total impressions.
- Median impressions: **3,396**.

Topic tags in the corpus include:

- oil: 29 posts
- WTI/CL: 8 posts
- crude: 4 posts
- Hormuz: 3 posts
- Brent: 6 posts

The largest social outlier was a May 6 liquidity-engine post with **3.6M impressions**. That post is important because it proves social reach and trading activity are not the same signal: it had massive impressions but negative WTI activity lift in the event window.

## Iteration History: How the Study Matured

### v0: Read-only feasibility

The first step was to determine whether the question could be studied at all.

The feasibility work established that:

- historical `@Ostium` posts could be collected through X full-archive search;
- Ostium Builder API could provide OHLC data for oil markets;
- DefiLlama could provide aggregate protocol proxies;
- Ostium's read-only SDK looked capable of providing market-specific fill activity.

The first read-only table joined social posts, oil OHLC data, and aggregate protocol metrics. It was useful, but not sufficient, because aggregate protocol metrics were not oil-specific.

### v1: Two hand-picked events

The first deeper report compared two cases:

1. **Apr 13 Hormuz/oil-shock post**
   - Strong social performance versus nearby non-oil posts.
   - Weak or negative per-market activity response.

2. **Mar 9–10 oil/Hormuz cluster**
   - Not a strong median social-outperformance case.
   - Much stronger WTI activity signal.

This introduced a useful distinction: some posts are social-reach events, while others coincide more closely with trading-activity events.

### v1.1: All 29 posts

The next version expanded from two hand-picked cases to the full 29-post corpus.

Key lesson: originals, replies, and retweets should be separable. Originals dominated reach, while replies and retweets were useful context but sometimes duplicated the same activity windows.

### v1.2: Event-study framing

v1.2 moved the analysis from ad hoc windows into a consistent event-study format:

- one row per post;
- 30-day pre-event baseline;
- 0–2d primary event window;
- 0–7d context window;
- WTI/Brent volatility and activity outcomes.

This made the study more reproducible and easier to compare across posts.

### v1.3: Post-time robustness

v1.3 added exact post-time windows:

- post timestamp through +48h;
- post timestamp through +72h;
- calendar 1–2d as an extra robustness layer.

This was useful because calendar-day event windows can include activity before a post went live. The exact post-time windows tested whether activity remained elevated after each post.

The post-level WTI event-study result was mixed:

- WTI 0–2d range lift was positive for **18/29** posts.
- WTI 0–2d activity lift was positive for **14/29** posts.
- WTI post +48h activity lift was positive for **12/29** posts.
- WTI post +72h activity lift was positive for **12/29** posts.

This was informative but not decisive. It showed strong cases, but it did not answer whether post days were different from similar no-post days.

### v1.4: Volatility-day control

v1.4 added the most important missing piece: a control comparison.

Instead of asking only “what happened around posts?”, v1.4 asked:

> On high-volatility oil-market days, was Ostium activity higher when Ostium posted oil content than when it did not?

High-volatility days were defined as days where:

- daily range lift was positive versus the rolling 30-day baseline; and
- daily range percentile was at or above the 75th percentile versus baseline.

This version created a market-day panel for WTI and Brent and flagged whether each day had an oil-related Ostium post.

## Main Result: WTI Shows a Positive Directional Relationship

The WTI control comparison is the strongest result in the project.

On high-volatility WTI days:

- Days with oil posts had median activity lift of **+74.0%**.
- Days without oil posts had median activity lift of **-9.3%**.
- Days with oil posts had median event notional/day of **$35.9M**.
- Days without oil posts had median event notional/day of **$6.5M**.

Across all eligible WTI days, not only high-volatility days:

- Post days had median activity lift of **+3.8%**.
- No-post days had median activity lift of **-69.0%**.
- Post days had median event notional/day of **$30.8M**.
- No-post days had median event notional/day of **$4.4M**.

Correlation checks were also directionally positive:

- WTI range-lift vs activity-lift correlation across eligible days: **0.46**.
- WTI range-lift vs activity-lift correlation across high-volatility days: **0.33**.
- WTI post-presence vs activity-lift correlation across eligible days: approximately **0.32**.
- WTI post-presence vs activity-lift correlation across high-volatility days: approximately **0.32**.

The best interpretation is:

> Ostium oil-related posting aligned with higher WTI activity during volatile oil windows. The relationship is positive and commercially meaningful, but still correlational.

## Brent Result: Interesting but Underpowered

Brent does not yet support the same conclusion.

The Brent sample is much smaller:

- Eligible Brent days: **26**.
- High-volatility Brent days: **5**.
- High-volatility Brent days with oil post: **1**.
- High-volatility Brent days without oil post: **4**.

The single high-volatility Brent post day had higher notional than the no-post median:

- With post: **$1.4M** median event notional/day.
- Without post: **$222k** median event notional/day.

But activity lift was negative in both groups:

- With post: **-75.1%**.
- Without post: **-98.6%**.

There were also zero positive activity-lift days in the high-volatility Brent subset.

This should be framed as underpowered/noisy rather than negative. Brent's market ramp and near-zero baselines make percentage changes unstable. More Brent history or a different event design would be needed.

## Social Performance: Reach and Activity Are Different Signals

The study found that social performance and trading activity should not be treated as the same outcome.

The Apr 13 Hormuz/oil-shock post was a strong social-performance case:

- 3,017 impressions.
- 48 engagement count.
- +419.3% impressions versus ±7d non-oil median.
- +860.0% engagement versus ±7d non-oil median.

But that same post did not show a strong activity lift.

The Mar 9–10 cluster was the opposite:

- Not a strong median social-outperformance case versus surrounding non-oil posts.
- Stronger WTI activity signal.

The May 6 liquidity-engine post had the most reach:

- 3.6M impressions.
- WTI activity lift: -54.5%.

This means the report should separate three concepts:

1. **Did the post reach people?**
2. **Was the market volatile?**
3. **Did trading activity rise?**

They are related in some cases, but not interchangeable.

## Answer to the Original Question

### Did Ostium post oil-related content during oil/Hormuz volatility windows?

Yes. The study found 29 oil/Hormuz-related posts across 21 dates.

### Did those posts perform well versus baseline?

Sometimes. The Apr 13 canonical Hormuz/oil-shock post clearly outperformed nearby non-oil posts socially. The Mar 9–10 cluster did not outperform by median social metrics. The largest social outlier, May 6, did not correspond to positive WTI activity lift.

### Did Ostium activity shift around those posts?

For WTI, yes directionally. The v1.4 control comparison shows materially higher WTI activity on high-volatility post days than on high-volatility no-post days.

For Brent, not enough evidence yet.

### Is there a positive correlation?

For WTI, yes. For Brent, inconclusive.

## What This Supports

The data supports the following claims:

- Ostium posted oil/Hormuz-related content during the study window.
- WTI volatility and WTI Ostium activity were positively correlated.
- High-volatility WTI days with oil posts had higher median activity than high-volatility WTI days without oil posts.
- High-volatility WTI days with oil posts had much higher median notional/day than high-volatility WTI days without oil posts.
- Social reach is not a reliable standalone proxy for trading activity.
- Brent remains underpowered and should not be overclaimed.

## What This Does Not Prove

The study does not prove that:

- Ostium posts caused trading activity to rise;
- higher impressions caused higher trading activity;
- the same result holds for Brent;
- the same result will hold for copper, gold, indices, FX, or crypto;
- the effect is independent of market volatility, campaign timing, or trader behavior.

## Caveats

### Correlation, not causation

The key limitation is endogeneity. Ostium may post because markets are volatile. Traders may trade because markets are volatile. Both posting and activity can be caused by the same underlying market regime.

### Small Brent sample

The Brent analysis has too few high-volatility post days to support a strong conclusion.

### Mixed post types

The corpus includes originals, replies, and retweets. That is useful for full account coverage but not every post type should be interpreted the same way.

### Duplicate windows

Multiple posts on the same date can share the same activity window. This is useful for post-level reporting but requires care when interpreting sample size.

### X API access

The analysis used fields available in the current X API environment. Future users may need equivalent X access to reproduce impressions/bookmarks.

## Final Conclusion

The completed oil/Hormuz analysis supports a clear but careful conclusion:

> Ostium oil-related posting showed a positive directional relationship with WTI trading activity during volatile oil windows. The strongest evidence is the v1.4 control comparison: high-volatility WTI days with oil posts had materially higher median activity and notional than high-volatility WTI days without posts. This is correlational, not causal. Brent remains underpowered and should not be treated as confirmed.

## Recommended Next Steps

For the public research package:

1. Turn this report into a web-native article with charts and interactive tables.
2. Add a reproducibility appendix explaining how to rerun the study.
3. Add a configurable study template so the same framework can be adapted to copper, gold, indices, FX, or crypto.
4. Package the repo with both Hermes-specific and generic agent instructions.
5. Build a dashboard that presents the report first, then allows parameter exploration.

For future research:

1. Cluster same-day/adjacent posts to avoid overcounting shared activity windows.
2. Separate original posts from replies and retweets in headline results.
3. Add a non-oil Ostium post baseline for social performance.
4. Extend the method to another market, likely copper, to test generality.
5. Keep the live recommendation engine as a later v2 once the static research kit is stable.
