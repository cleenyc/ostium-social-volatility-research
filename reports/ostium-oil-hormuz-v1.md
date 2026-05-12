# Ostium Oil/Hormuz V1 Report

Date: 2026-05-11

## Scope

This v1 joins official `@Ostium` oil-related X posts, Ostium Builder OHLC, DefiLlama aggregate protocol proxies, and read-only Ostium SDK per-market fills for WTI and Brent. No Dune was used.

## Source coverage

- X oil-post sample: 29 posts; total impressions 3,744,063.
- SDK activity: `OstiumClient.createReadOnly()` + `getFillsByTime({ user: 'ALL', pairId, ... })`.
- Pair mapping: WTI/CL pairId `7`; Brent pairId `55`.
- Activity metric validation: SDK `Fill.px` is execution price and `Fill.szi` is documented trade size in base-asset units; SDK source maps `tradeNotional` to `szi`. Therefore `abs(px * szi)` is used as USD execution notional for WTI/Brent fills.

## Event 1 — Apr 13 canonical Hormuz/oil-shock post

Social baseline: canonical post had 3,017 impressions and 48 engagement vs ±7d non-oil medians of 581 impressions and 5 engagement.
- Impression lift vs non-oil median: +419.3%.
- Engagement lift vs non-oil median: +860.0%.
- WTI SDK activity: event notional/day $6,555,474 vs pre7/day $29,037,187 (-77.4%); post7/day $2,310,971 (-92.0%).
  - fills/day: event 365.0 vs pre7 222.3 (+64.2%). opening fees/day: event $5,176 vs pre7 $21,277 (-75.7%).
- BRENT SDK activity: event notional/day $131,568 vs pre7/day $23,549,876 (-99.4%); post7/day $122,184 (-99.5%).
  - fills/day: event 51.0 vs pre7 103.9 (-50.9%). opening fees/day: event $80 vs pre7 $14,581 (-99.4%).
Interpretation: strong social outperformance, but per-market activity is lower than the preceding week for both WTI and Brent. This supports the earlier aggregate finding: Apr 13 is a social-performance case, not a clear protocol-activity-lift case.

## Event 2 — Mar 9–10 oil/Hormuz cluster

Social baseline: oil-cluster median impressions 1,125 vs non-oil baseline 1,418; median engagement 5 vs baseline 10.
- Impression delta vs non-oil median: -20.7%.
- Engagement delta vs non-oil median: -50.0%.
- WTI SDK activity: event notional/day $194,366,669 vs pre7/day $52,733,083 (+268.6%); post7/day $36,257,786 (-31.2%).
  - fills/day: event 1899.0 vs pre7 642.9 (+195.4%). opening fees/day: event $143,730 vs pre7 $44,288 (+224.5%).
- BRENT SDK activity: event notional/day $0 vs pre7/day $0 (n/a); post7/day $0 (n/a).
  - fills/day: event 0.0 vs pre7 0.0 (n/a). opening fees/day: event $0 vs pre7 $0 (n/a).
Interpretation: not a social median-outperformance case, but WTI activity was materially elevated per day during the cluster. Brent had no fills in the tested window, so the activity signal is WTI-specific.

## Top oil posts by impressions

- 2026-05-06 — 3,615,280 impressions — https://x.com/ostium/status/2052072913566576963 — What the new liquidity engine means for you (the director's cut). Oil, gold, AI, and more. Try Ostium today.
- 2026-03-23 — 30,682 impressions — https://x.com/ostium/status/2036180862891651128 — BRENT OIL LIVE NOW ON OSTIUM. https://t.co/GeERkR9T9j
- 2026-03-24 — 11,512 impressions — https://x.com/ostium/status/2036488094296449322 — Ostium has no order books for a reason. Our traders today are sizing $2.5M+ positions across oil and gold, all at &lt;5bps spread. Access the most liquid global markets with the best execution onchain. https://t.co/L2qlGiuYbZ https://t.co/…
- 2026-03-03 — 11,345 impressions — https://x.com/ostium/status/2028934137235558417 — One of the smart money traders on Ostium just rotated out of silver into crude oil. $774M volume on XAG. +$1.6M realized. Moved every dollar into CL longs $5M clips at a time. Currently sitting on ~$20M. Copy trade XAG, CL, and 200+ market…
- 2026-04-03 — 10,028 impressions — https://x.com/ostium/status/2040053134899204248 — Ostium in The Wall Street Journal. Trade oil, gold, and stocks onchain from the most liquid markets in the world. https://t.co/1F8WWV9tIW

## Bottom-line v1 read

- **Apr 13:** social signal strong; per-market activity response weak/negative vs pre-window.
- **Mar 9–10:** social median signal weak; WTI per-market activity strong and aligns with the protocol-fee spike previously observed.
- The likely distinction is useful: some posts are high-engagement narrative posts, while others appear reactive/coincident with actual market-specific trading activity.
- Causality is still not established; v1 supports event-window correlation only.

## Generated files

- `reports/ostium-oil-hormuz-v1.md`
- `reports/ostium-oil-hormuz-event-table.csv`
- `data/processed/activity_windows.csv`
- `data/processed/activity_daily.csv`
- `data/processed/activity_response.csv`
