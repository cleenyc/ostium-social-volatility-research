# Ostium Social Volatility Research Report — Phase 1 Package

Date: 2026-05-12  
Status: Draft v1 research-report package, generated from the completed oil/Hormuz analysis through v1.4.  
Project: Ostium Social Volatility Research Kit

## Executive Summary

This research project began with a narrow question:

> During a defined oil/Hormuz volatility window, did Ostium post oil-related content, how did those posts perform versus baseline, and did Ostium volume/activity shift around those posts?

After progressing from initial read-only feasibility work through the v1.3 event study and v1.4 volatility-day control report, the project is now sufficiently developed to answer the question directionally for WTI.

The strongest current conclusion is:

> Ostium oil/Hormuz posting showed a positive directional/correlational relationship with WTI activity during oil-volatility windows. High-volatility WTI days with oil-related Ostium posts had materially higher median activity and notional than high-volatility WTI days without oil-related posts.

This is not causal proof. Ostium posts were not randomized, post timing is likely endogenous to market conditions and campaign decisions, and the same volatility that motivates posting may also motivate traders. The finding should therefore be framed as correlational evidence that posting aligned with, and may have amplified, WTI trading activity during volatile oil windows.

Brent is not yet strong enough for the same conclusion. Brent coverage is smaller, Brent activity appears affected by launch/ramp dynamics, and the v1.4 high-volatility Brent comparison has only five high-volatility days, only one of which has an oil post.

## Research Question

The original working question was:

> Around a defined Strait of Hormuz / oil volatility window, did Ostium post oil-related content, how did those posts perform vs baseline, and did any Ostium volume/activity shift around those posts?

As the project matured, this decomposed into five analytical questions:

1. Did `@Ostium` post oil/Hormuz-related content during relevant volatility windows?
2. Did those posts perform well socially?
3. Were WTI or Brent volatility measures elevated around those posts?
4. Did Ostium WTI/Brent activity rise around those posts?
5. Compared with similar high-volatility days without posts, were post days associated with higher activity?

The final v1.4 answer relies most heavily on question 5 because it introduces the missing control group: high-volatility market days with no oil-related Ostium post.

## Source Files and Evidence Base

This report synthesizes the following local artifacts:

- Project doc: `local-project-docs/ostium-social-volatility-backtest.md`
- Feasibility brief: `local-project-docs/ostium-social-volatility-feasibility-2026-05-11.md`
- Project Builder plan: `local-project-docs/ostium-social-volatility-backtest-project-builder-plan.md`
- Read-only spike: `local-provenance/2026-05-11-readonly-spike/ostium_oil_hormuz_readonly_spike_2026-05-11.md`
- Apr 13 inference note: `local-provenance/2026-05-11-readonly-spike/ostium_two_inferences_note_2026-05-11.md`
- Mar 9–10 cluster spike: `local-provenance/2026-05-11-readonly-spike/ostium_mar9_10_cluster_pm7_spike_2026-05-11.md`
- v1 report: `reports/ostium-oil-hormuz-v1.md`
- v1.1 all-post report: `reports/ostium-oil-hormuz-all-posts-v1_1.md`
- v1.2 event-study report: `reports/ostium-oil-hormuz-event-study-v1_2.md`
- v1.3 event-study report: `reports/ostium-oil-hormuz-event-study-v1_3.md`
- v1.4 volatility-control report: `reports/ostium-oil-hormuz-volatility-control-v1_4.md`
- v1.3 event-study CSV: `reports/ostium-oil-hormuz-event-study-v1_3.csv`
- v1.4 volatility-control CSV: `reports/ostium-oil-hormuz-volatility-control-v1_4.csv`

## Data Sources

### X / Twitter

The social dataset came from X full-archive search, using the query:

```text
from:Ostium oil
```

The working 90-day query returned 29 `@Ostium` posts across 21 dates. The social fields available in the collected data included timestamps, text, tweet IDs, URLs, post type, public engagement counts, bookmarks where available, and impressions.

Important source discovery:

- `xurl search` should be treated as recent-search only because it maps to `/2/tweets/search/recent` semantics.
- Historical discovery used the raw full-archive endpoint `/2/tweets/search/all` with app-only auth.
- X impressions/bookmarks were available in the current responses, but future availability depends on auth/tier behavior.

### Ostium Builder API OHLC

Market candles came from the Ostium Builder API. The feasibility pass verified daily OHLC for market symbols including:

- `CL-USD` — crude oil / WTI proxy.
- `BRENT-USD` — Brent.
- `HG-USD` — copper, kept as future comparison target.
- Additional pairs such as `XAU-USD`, `XAG-USD`, `SPX-USD`, `NDX-USD`, `BTC-USD`, `ETH-USD`, and FX pairs.

A key data-source lesson was to use Ostium's own pair symbols from `/v1/prices`; do not assume external ticker names such as `WTI-USD`, `COPPER-USD`, or `US500-USD`.

### Ostium SDK / Per-Market Activity

The project ultimately used read-only Ostium SDK activity windows via:

```text
OstiumClient.createReadOnly()
getFillsByTime({ user: 'ALL', pairId, ... })
```

Pair mapping used in the analysis:

- WTI / CL: pairId `7`
- Brent: pairId `55`

The primary per-market activity metric is estimated USD execution notional:

```text
abs(px * szi)
```

This is documented in the project README as validated against `@ostium/builder-sdk` types/source: `Fill.px` is execution price, `Fill.szi` is trade size in base-asset units, and the SDK maps subgraph `tradeNotional` to `szi`.

### DefiLlama Aggregate Protocol Proxies

Early v0/v1 work used DefiLlama as an aggregate protocol proxy for TVL, fees/revenue, and open interest. This was useful for initial feasibility and event identification, but it was not oil-specific. Later versions shifted the core activity outcome to SDK-derived WTI/Brent per-market fills.

## Methodology Evolution

### Inception / Feasibility

The project started as a scoping idea: test whether Ostium social post performance aligns with market volatility and protocol activity.

Initial blockers were:

- whether historical X data was accessible;
- whether Ostium had usable price/market data;
- whether Ostium protocol activity could be measured without paid Dune or private APIs;
- how to define volatility and event windows.

The feasibility brief concluded that a narrow oil/Hormuz v0 was viable because:

- X full-archive search worked via `xurl --auth app`;
- the last-90-day `from:Ostium oil` query returned 29 posts;
- Ostium Builder API OHLC worked for `CL-USD` and `BRENT-USD`;
- DefiLlama public endpoints worked for aggregate proxies;
- Ostium SDK docs exposed read-only fills methods that looked suitable for per-market activity.

### Read-Only v0 Spike

The first read-only spike joined:

- 29 oil-related `@Ostium` X posts;
- Ostium Builder API daily OHLC for `CL-USD` and `BRENT-USD`;
- DefiLlama aggregate protocol proxies.

Key read-only finding:

- The data was sufficient for a lightweight event-window analysis.
- It could show whether posts clustered around elevated oil-market sessions and whether aggregate protocol proxies moved around those days.
- It could not yet attribute protocol volume specifically to oil markets.

The spike highlighted two candidate cases:

1. Apr 13 canonical Hormuz/oil-shock post: strong social outperformance but weak/negative aggregate protocol response.
2. Mar 9–10 oil/Hormuz cluster: weaker social median performance but much stronger aggregate protocol-fee response.

### Apr 13 Baseline Note

The Apr 13 canonical Hormuz/oil-shock post had:

- 3,017 impressions;
- 48 engagement count;
- engagement rate of 1.59%.

Against surrounding non-oil `@Ostium` posts:

- ±7d non-oil median impressions: 581; canonical post lift: +419.3%.
- ±7d non-oil median engagement: 5; canonical post lift: +860.0%.
- ±14d non-oil median impressions: 333.5; canonical post lift: +804.6%.
- ±14d non-oil median engagement: 4; canonical post lift: +1100.0%.

But aggregate protocol proxies did not show a clear lift:

- Fees: day-of $99,947 vs pre-7d average $129,048; post-7d average $102,664.
- Open interest: day-of $127.5M vs pre-7d average $147.4M; post-7d average $147.0M.
- TVL: day-of $56.7M vs pre-7d average $60.6M; post-7d average $58.7M.

Interpretation: Apr 13 was a social-performance case, not a clear protocol-activity-lift case.

### Mar 9–10 Cluster Spike

The Mar 9–10 cluster was tested against surrounding non-oil posts in a ±7d window.

Social result:

- Posts pulled in ±7d window: 49.
- Oil posts on Mar 9–10: 5.
- Non-oil baseline posts in window: 36.
- Median impressions for Mar 9–10 oil posts: 1,125.
- Median impressions for surrounding non-oil posts: 1,418.
- Median engagement for Mar 9–10 oil posts: 5.
- Median engagement for surrounding non-oil posts: 10.

So the cluster did not outperform socially by median.

Aggregate protocol proxy result:

- Fees: pre-7d average $145,977; Mar 9–10 average $739,858; lift +406.8%.
- Open interest: pre-7d average $216.2M; Mar 9–10 average $197.8M; change -8.5%.
- TVL: pre-7d average $88.9M; Mar 9–10 average $91.3M; lift +2.7%.

Interpretation: Mar 9–10 was a better protocol-activity candidate than Apr 13, not because it outperformed socially, but because it coincided with much stronger activity signals.

### v1 — Two Hand-Picked Event Cases With SDK Activity

v1 joined official `@Ostium` oil-related X posts, Ostium Builder OHLC, DefiLlama aggregate proxies, and read-only Ostium SDK per-market fills for WTI and Brent.

Key v1 results:

- Apr 13: strong social signal but negative WTI/Brent activity versus pre-window.
- Mar 9–10: weaker social median signal but strong WTI per-market activity during the cluster.

The report framed the emerging distinction:

> Some posts are high-engagement narrative posts, while others appear reactive/coincident with actual market-specific trading activity.

### v1.1 — All-Posts Expansion

v1.1 expanded from two hand-picked events to all 29 oil posts from the 90-day query.

Coverage:

- 29 posts across 21 unique dates.
- Post types: 20 originals, 5 replies, 4 retweets.
- Categories: oil 29, WTI/CL 8, crude 4, Hormuz 3, Brent 6.
- Total impressions: 3,744,063.
- SDK windows collected: 126.

Key v1.1 finding:

- Originals dominated reach.
- Replies and retweets added useful context but needed to remain separable.
- The strongest protocol-activity windows remained WTI-heavy.
- Brent appeared concentrated around launch/Brent-specific posts rather than the Mar 9–10 Hormuz cluster.

### v1.2 — Event-Study Framing

v1.2 converted the analysis into a lightweight event study.

Method:

- Event unit: each `@Ostium` oil/Hormuz-related post.
- Baseline: 30 calendar days before event date, end-exclusive.
- Primary event window: event date through two days after (`0–2d`).
- Secondary context window: event date through seven days after (`0–7d`).
- Outcomes: X metrics, WTI/Brent volatility, WTI/Brent SDK activity.

Why this mattered:

- The primary window became more standardized.
- The 30-day baseline reduced arbitrary pre/post framing.
- The report could compare all events on a consistent basis.

### v1.3 — Post-Time Robustness Event Study

v1.3 retained the 0–2d primary event window and added exact post-time robustness checks:

- exact tweet timestamp through +48h;
- exact tweet timestamp through +72h;
- calendar `1–2d` as an additional robustness layer.

Coverage:

- 29 posts across 21 dates.
- Post types: 20 originals, 5 replies, 4 retweets.
- Activity windows collected: 342, including calendar windows and exact post-time windows.

Post-level v1.3 WTI summary:

- WTI 0–2d range lift: median +8.9%; mean +61.3%; positive for 18/29 posts.
- WTI 0–2d notional lift: median -2.0%; mean +197.1%; positive for 14/29 posts.
- WTI exact post +48h notional lift: median -48.4%; mean +156.6%; positive for 12/29 posts.
- WTI exact post +72h notional lift: median -11.3%; mean +113.1%; positive for 12/29 posts.

This showed the post-level event study was mixed. Averages were pulled upward by strong WTI events, but medians were not uniformly positive. That meant the project still needed a control comparison.

### v1.4 — Volatility-Day Control Comparison

v1.4 added the missing control group.

Core question:

> On high oil-volatility days, was Ostium activity higher when Ostium posted oil content than when it did not?

Method:

- Markets: WTI over all available WTI OHLC days; Brent over all available Brent OHLC days.
- Eligible market days required at least 10 prior OHLC observations in the 30-day rolling baseline.
- High-volatility definition: daily range lift > 0 and daily range percentile vs rolling baseline >= 75th percentile.
- Post flag: date has at least one oil/Hormuz-related `@Ostium` post from the v1.3 event table.
- Activity outcome: Ostium SDK notional/day in the calendar `0–2d` window vs prior 30-day activity baseline.

Coverage:

- Oil posts available: 29 posts across 21 dates.
- WTI: 75 eligible market days; 25 high-volatility days.
- Brent: 26 eligible market days; 5 high-volatility days.

## Final Results

### WTI: Positive Directional Correlation

v1.4 provides the strongest current evidence for WTI.

Among high-volatility WTI days:

- With oil post: 10 days.
- Without oil post: 15 days.
- Median activity lift with oil post: +74.0%.
- Median activity lift without oil post: -9.3%.
- Mean activity lift with oil post: +402.2%.
- Mean activity lift without oil post: +105.0%.
- Positive activity-lift days with oil post: 5/10.
- Positive activity-lift days without oil post: 6/15.
- Median event notional/day with oil post: $35.9M.
- Median event notional/day without oil post: $6.5M.

Across all eligible WTI days:

- Post days: 19.
- No-post days: 56.
- Median activity lift on post days: +3.8%.
- Median activity lift on no-post days: -69.0%.
- Mean activity lift on post days: +230.8%.
- Mean activity lift on no-post days: -1.0%.
- Median event notional/day on post days: $30.8M.
- Median event notional/day on no-post days: $4.4M.

Correlation checks:

- WTI range-lift vs activity-lift correlation across eligible days: 0.46 (n=75).
- WTI range-lift vs activity-lift correlation across high-volatility days: 0.33 (n=25).
- WTI post-presence vs activity-lift correlation across eligible days: about 0.32.
- WTI post-presence vs activity-lift correlation across high-volatility days: about 0.32.

Interpretation:

WTI shows a positive directional relationship between volatility, oil/Hormuz posting, and Ostium activity. The strongest framing is not simply “posts happened and volume rose.” The stronger framing is:

> During high-volatility WTI days, days with oil-related Ostium posts had materially higher median activity and notional than high-volatility WTI days without oil-related posts.

### Brent: Underpowered / Noisy

Brent does not support the same conclusion yet.

Brent coverage:

- Eligible Brent days: 26.
- High-volatility Brent days: 5.
- High-volatility Brent days with oil post: 1.
- High-volatility Brent days without oil post: 4.

High-volatility Brent comparison:

- Median activity lift with oil post: -75.1%.
- Median activity lift without oil post: -98.6%.
- Positive activity-lift days with oil post: 0/1.
- Positive activity-lift days without oil post: 0/4.
- Median event notional/day with oil post: $1.4M.
- Median event notional/day without oil post: $222k.

Correlation checks:

- Brent range-lift vs activity-lift correlation across eligible days: -0.19 (n=26).
- Brent range-lift vs activity-lift correlation across high-volatility days: 0.34 (n=5).

Interpretation:

The one high-volatility Brent post day had higher notional than the no-post median, but activity lift was still negative. With only five high-volatility Brent days and one post day, this should be treated as underpowered and noisy. Brent launch/ramp dynamics also complicate percentage-lift interpretation because near-zero baselines can create extreme values.

### Social Reach Does Not Cleanly Predict Activity

The social reach story is separate from the activity story.

Across the 29 v1.3 posts:

- Total impressions: 3,744,063.
- Median impressions: 3,396.
- Mean impressions: 129,106.
- Maximum impressions: 3,615,280.

The largest social reach post was May 6:

- 3,615,280 impressions.
- WTI range lift: +27.4%.
- WTI activity lift: -54.5%.

This outlier shows that social reach alone does not map cleanly to WTI trading activity. The project can say oil-related posting aligned with WTI activity in volatility windows, but it should not say that higher impressions reliably drove higher activity.

## Answer to the Original Question

### Did Ostium post oil-related content during the defined oil/Hormuz volatility window?

Yes.

The full-archive query found 29 oil/Hormuz-related `@Ostium` posts across 21 dates. The post set included originals, replies, and retweets, with originals making up the largest share.

### How did those posts perform vs baseline?

The answer depends on which baseline and which event.

- Apr 13 canonical Hormuz/oil-shock post strongly outperformed nearby non-oil posts socially.
- Mar 9–10 cluster did not outperform surrounding non-oil posts by median impressions or engagement.
- The highest-reach post, May 6, dominated impressions but did not coincide with positive WTI activity lift.

So the social-performance story is mixed. Some oil posts outperformed socially; social reach is not itself a reliable proxy for protocol activity.

### Did Ostium volume/activity shift around those posts?

For WTI, yes directionally.

v1.3 post-level event-study metrics were mixed, but v1.4 added the key control comparison. High-volatility WTI days with oil posts had substantially higher median activity lift and median notional/day than high-volatility WTI days without oil posts.

For Brent, the evidence remains too sparse and noisy.

### Is there a positive correlation?

For WTI, yes.

The clearest current statement is:

> There is positive directional/correlational evidence that Ostium oil/Hormuz posting aligned with higher WTI activity during oil-volatility windows.

The project should not claim:

> Ostium posts caused the volume increase.

## What Is Supported vs Not Supported

### Supported

The current data supports these statements:

- Ostium posted oil/Hormuz-related content during the study period.
- The oil post corpus contains 29 posts across 21 dates.
- WTI volatility and WTI Ostium activity were positively correlated across eligible days.
- High-volatility WTI post days had higher median activity lift than high-volatility WTI no-post days.
- High-volatility WTI post days had much higher median event notional/day than high-volatility WTI no-post days.
- Brent evidence is limited and should be treated as underpowered.
- Social impressions are a separate signal and do not cleanly predict WTI activity.

### Not Supported

The current data does not support these stronger claims:

- Ostium posts caused trading activity to rise.
- High-impression posts reliably generated higher trading activity.
- Brent posting/activity relationship is established.
- The observed WTI relationship is independent of market volatility, campaign timing, or trader behavior.
- The result generalizes automatically to other markets such as copper, gold, indices, or FX without rerunning the study.

## Caveats

1. **Correlation, not causation**
   - Posting was not randomized.
   - Posts may be reactive to the same volatility that drives trading.
   - Campaign decisions may co-move with market activity.

2. **Post-type mixing**
   - The 29-post corpus includes originals, replies, and retweets.
   - Originals dominate reach; replies/retweets may duplicate event windows or reflect different intent.

3. **Same-day duplicate windows**
   - Multiple posts on the same date share the same calendar activity window.
   - This is useful for post-level records but can overstate independence unless clustered.

4. **Brent sample size and ramp effects**
   - Brent has fewer eligible days and fewer high-volatility post days.
   - New market launch/ramp periods create near-zero baselines and unstable percentage lifts.

5. **X API/tier dependency**
   - Impressions/bookmarks were available in this environment, but future users may need equivalent access.

6. **Public packaging**
   - The planned public version should use tweet links and reproducible instructions rather than committing local auth artifacts or secrets.

## Phase 1 Research Report Package Conclusion

The first analytical phase is complete enough to become a full research-report package.

The headline public-facing conclusion should be:

> In the oil/Hormuz study, Ostium oil-related posting showed a positive directional relationship with WTI trading activity during volatile oil windows. The strongest evidence comes from the v1.4 volatility-day control: high-volatility WTI days with oil posts had materially higher median activity and notional than high-volatility WTI days without posts. The result is correlational, not causal, and Brent remains underpowered/noisy.

## Recommended Next Report Work

Before this becomes a polished public report, the next Phase 1 refinements should be:

1. Convert this draft into a narrative public report with cleaner prose and charts.
2. Add figure/table placeholders for dashboard reuse:
   - WTI high-vol post vs no-post comparison.
   - Brent high-vol post vs no-post comparison.
   - v1.3 event-study top cases.
   - social reach vs WTI activity outlier chart.
   - iteration timeline v0 -> v1.4.
3. Add a methodology appendix with exact commands and source paths.
4. Add a public-safe data disclosure note: tweet links are featured; secrets/auth files excluded.
5. Decide whether to include full v1.3/v1.4 CSVs publicly or provide reproducible generation instructions plus sample fixtures.

## Source Inventory for Phase 1

Primary reports:

- `reports/ostium-oil-hormuz-v1.md`
- `reports/ostium-oil-hormuz-all-posts-v1_1.md`
- `reports/ostium-oil-hormuz-event-study-v1_2.md`
- `reports/ostium-oil-hormuz-event-study-v1_3.md`
- `reports/ostium-oil-hormuz-volatility-control-v1_4.md`

Primary CSVs:

- `reports/ostium-oil-hormuz-event-study-v1_3.csv`
- `reports/ostium-oil-hormuz-volatility-control-v1_4.csv`
- `data/processed/market_volatility_event_windows.csv`
- `data/processed/event_study_activity_windows.csv`
- `data/processed/volatility_control_days.csv`

Primary scripts:

- `scripts/collect_event_study_activity_windows.mjs`
- `scripts/run_event_study_report.py`
- `scripts/collect_volatility_control_activity_windows.mjs`
- `scripts/run_volatility_control_report.py`

Recommended reproducibility commands from the repo README:

```bash
node scripts/collect_event_study_activity_windows.mjs
python3 scripts/run_event_study_report.py

node scripts/collect_volatility_control_activity_windows.mjs
python3 scripts/run_volatility_control_report.py

python3 -m pytest -q
```
