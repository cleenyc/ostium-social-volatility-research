# Ostium Oil/Hormuz V1.3 Event-Study Report

Date: 2026-05-12

## Method

- Event unit: each `@Ostium` oil/Hormuz-related post from the 90-day full-archive query.
- Calendar baseline: 30 calendar days before the event date, end-exclusive.
- Primary event window remains event date through two days after (`0–2d`, 3 calendar days total).
- Post-time activity windows: exact tweet timestamp through +48h and +72h, compared with the exact 30 days before tweet timestamp.
- Robustness activity window: calendar `1–2d`, used as an extra layer rather than the primary framing.
- Secondary context window: event date through seven days after (`0–7d`), not the headline window.
- Outcomes: X social metrics, WTI/Brent market volatility, and Ostium SDK WTI/Brent trading activity.
- Market volatility metrics: intraday range % and absolute open-to-close return %, each compared with the 30-day baseline.
- Activity metrics: SDK fill notional/day and fills/day compared with the 30-day baseline.
- Activity rankings use notional/day as the primary economic signal because new Brent launch/ramp periods can have near-zero baselines and extreme percentage lifts.

## Coverage

- Posts: 29 across 21 unique event dates.
- Post types: {'retweet': 4, 'original': 20, 'reply': 5}.
- Oil categories: {'oil': 29, 'wti_cl': 8, 'crude': 4, 'hormuz': 3, 'brent': 6}.
- Activity windows collected: 342; includes calendar windows and per-post exact post-time windows; WTI pairId 7, Brent pairId 55.
- Partial 0–7d context windows: 2; primary 0–2d remains the continuity window.

## Strongest combined cases
- 2026-03-09 [original] impressions 3,477; WTI range lift +439.4%; Brent range lift n/a; WTI activity 0–2d +821.1%, post+48h +898.9%; Brent activity 0–2d n/a, post+48h n/a; https://x.com/ostium/status/2030992222892839275 — The Strait of Hormuz carries ~20% of global oil supply, and rising Iran tensions are putting supply chains under pressure. The Chokepoint Boost Window is live. Trade Oil, Silver, Gold, Copper &amp; USD/JPY with double points this week. htt…
- 2026-03-03 [original] impressions 11,345; WTI range lift +169.6%; Brent range lift n/a; WTI activity 0–2d +1444.7%, post+48h +789.5%; Brent activity 0–2d n/a, post+48h n/a; https://x.com/ostium/status/2028934137235558417 — One of the smart money traders on Ostium just rotated out of silver into crude oil. $774M volume on XAG. +$1.6M realized. Moved every dollar into CL longs $5M clips at a time. Currently sitting on ~$20M. Copy trade XAG, CL, and 200+ market…
- 2026-03-23 [original] impressions 30,682; WTI range lift +33.3%; Brent range lift +73.7%; WTI activity 0–2d -10.8%, post+48h -72.5%; Brent activity 0–2d n/a, post+48h +948558.2%; https://x.com/ostium/status/2036180862891651128 — BRENT OIL LIVE NOW ON OSTIUM. https://t.co/GeERkR9T9j
- 2026-03-24 [original] impressions 11,512; WTI range lift -19.8%; Brent range lift +7.8%; WTI activity 0–2d -64.2%, post+48h -57.0%; Brent activity 0–2d +651626.9%, post+48h +2184.0%; https://x.com/ostium/status/2036488094296449322 — Ostium has no order books for a reason. Our traders today are sizing $2.5M+ positions across oil and gold, all at &lt;5bps spread. Access the most liquid global markets with the best execution onchain. https://t.co/L2qlGiuYbZ https://t.co/…
- 2026-03-30 [original] impressions 3,677; WTI range lift -20.6%; Brent range lift +1.5%; WTI activity 0–2d +39.5%, post+48h +54.9%; Brent activity 0–2d +1385.2%, post+48h +714.7%; https://x.com/ostium/status/2038723410470076589 — This trader went all in on oil. Four positions totalling $25.61M across Brent and WTI. All opened this morning at 8AM est. Two of those trades shown below. 0.0286-0.045% slippage. Up +$640.7k. https://t.co/rOnPgXkwK6
- 2026-03-10 [original] impressions 3,396; WTI range lift +152.0%; Brent range lift n/a; WTI activity 0–2d +288.9%, post+48h +301.6%; Brent activity 0–2d n/a, post+48h n/a; https://x.com/ostium/status/2031411333053428214 — $180M in Oil volume on Ostium last 24hrs. 498 unique traders. 3,294 trades. Largest single trade: $8M, Price impact: 4.31bps Will the volatility continue or is the war over? https://t.co/iRdgOIRIS0
- 2026-03-28 [original] impressions 9,179; WTI range lift -58.4%; Brent range lift -51.6%; WTI activity 0–2d -67.4%, post+48h -51.6%; Brent activity 0–2d +510.5%, post+48h +807.7%; https://x.com/ostium/status/2037929986305241286 — CL (WTI) is the benchmark for the US light oil market. Brent is the benchmark for the wider light oil market across Europe, Africa, and the Middle East. Trade both on Ostium. https://t.co/9aHzjMzOqU
- 2026-03-05 [original] impressions 5,795; WTI range lift +288.8%; Brent range lift n/a; WTI activity 0–2d +150.1%, post+48h +51.9%; Brent activity 0–2d n/a, post+48h n/a; https://x.com/ostium/status/2029628328076800335 — Same trader closed the entire position Tuesday. Re-entered today. $14.5M in crude longs across 5 positions. Oil is the highest its been since June 2025. Iran struck a tanker yesterday. What do they know? https://t.co/AT2F2sMebr https://t.c…

## Highest market-volatility alignment
- 2026-03-09 impressions 3,477; WTI 0–2d range 21.4% vs baseline 4.0% (+439.4%); Brent 0–2d range n/a% vs baseline n/a% (n/a); https://x.com/ostium/status/2030992222892839275 — The Strait of Hormuz carries ~20% of global oil supply, and rising Iran tensions are putting supply chains under pressure. The Chokepoint Boost Window is live. Trade Oil, Silver, Gold, Copper &amp; USD/JPY with double points this week. htt…
- 2026-03-09 impressions 0; WTI 0–2d range 21.4% vs baseline 4.0% (+439.4%); Brent 0–2d range n/a% vs baseline n/a% (n/a); https://x.com/ostium/status/2031011633909432824 — RT @Copin_io: $5.6M Oil Trading Masterclass on @ostium! 🛢️ This wallet started trading $CL (crude oil) in late February and had alread…
- 2026-03-05 impressions 5,795; WTI 0–2d range 12.7% vs baseline 3.3% (+288.8%); Brent 0–2d range n/a% vs baseline n/a% (n/a); https://x.com/ostium/status/2029628328076800335 — Same trader closed the entire position Tuesday. Re-entered today. $14.5M in crude longs across 5 positions. Oil is the highest its been since June 2025. Iran struck a tanker yesterday. What do they know? https://t.co/AT2F2sMebr https://t.c…
- 2026-03-03 impressions 11,345; WTI 0–2d range 7.7% vs baseline 2.9% (+169.6%); Brent 0–2d range n/a% vs baseline n/a% (n/a); https://x.com/ostium/status/2028934137235558417 — One of the smart money traders on Ostium just rotated out of silver into crude oil. $774M volume on XAG. +$1.6M realized. Moved every dollar into CL longs $5M clips at a time. Currently sitting on ~$20M. Copy trade XAG, CL, and 200+ market…
- 2026-03-10 impressions 3,396; WTI 0–2d range 12.9% vs baseline 5.1% (+152.0%); Brent 0–2d range n/a% vs baseline n/a% (n/a); https://x.com/ostium/status/2031411333053428214 — $180M in Oil volume on Ostium last 24hrs. 498 unique traders. 3,294 trades. Largest single trade: $8M, Price impact: 4.31bps Will the volatility continue or is the war over? https://t.co/iRdgOIRIS0
- 2026-03-23 impressions 30,682; WTI 0–2d range 10.1% vs baseline 7.6% (+33.3%); Brent 0–2d range 6.3% vs baseline 3.6% (+73.7%); https://x.com/ostium/status/2036180862891651128 — BRENT OIL LIVE NOW ON OSTIUM. https://t.co/GeERkR9T9j
- 2026-03-31 impressions 72; WTI 0–2d range 9.5% vs baseline 8.7% (+8.9%); Brent 0–2d range 8.4% vs baseline 5.5% (+55.0%); https://x.com/ostium/status/2039103046060527692 — @Yoliu_ We don't have native order books. It is an intentional design. This is because we believe RWAs and traditional assets like gold, oil, stocks already trade on ultra liquid markets. Recreating that onchain would further fragment liqu…
- 2026-03-27 impressions 4,165; WTI 0–2d range 5.1% vs baseline 8.5% (-39.9%); Brent 0–2d range 7.5% vs baseline 5.6% (+35.0%); https://x.com/ostium/status/2037520026341650937 — In the last 4 hours on Ostium, this smart money wallet: Scaled into three $14.71M total longs on oil (BRENT) Opened one $3.95M short on silver (XAG) 8-15x leverage. Low slippage. All in the money. Trade commodities onchain from the most li…

## Highest Ostium WTI/Brent activity signals
- 2026-03-09 impressions 3,477; WTI 0–2d $150,586,882 (+821.1%), post+48h $185,494,401 (+898.9%); Brent 0–2d $0 (n/a), post+48h $0 (n/a); https://x.com/ostium/status/2030992222892839275 — The Strait of Hormuz carries ~20% of global oil supply, and rising Iran tensions are putting supply chains under pressure. The Chokepoint Boost Window is live. Trade Oil, Silver, Gold, Copper &amp; USD/JPY with double points this week. htt…
- 2026-03-09 impressions 0; WTI 0–2d $150,586,882 (+821.1%), post+48h $185,279,296 (+896.7%); Brent 0–2d $0 (n/a), post+48h $0 (n/a); https://x.com/ostium/status/2031011633909432824 — RT @Copin_io: $5.6M Oil Trading Masterclass on @ostium! 🛢️ This wallet started trading $CL (crude oil) in late February and had alread…
- 2026-03-17 impressions 4,416; WTI 0–2d $152,672,223 (+394.7%), post+48h $155,668,255 (+335.4%); Brent 0–2d $0 (n/a), post+48h $0 (n/a); https://x.com/ostium/status/2034034779063198173 — This smart money trader on Ostium just opened four $9.8M positions. $39.4M in oil at only 4.5 bps. The Strait of Hormuz is closed. Oil is still open to trade. https://t.co/701UpboL1c
- 2026-03-17 impressions 1,217; WTI 0–2d $152,672,223 (+394.7%), post+48h $155,668,255 (+335.4%); Brent 0–2d $0 (n/a), post+48h $0 (n/a); https://x.com/ostium/status/2034034791943967135 — Trade Oil on Ostium: https://t.co/9uZoci4yPF
- 2026-03-16 impressions 2,586; WTI 0–2d $105,935,194 (+245.4%), post+48h $140,367,549 (+356.3%); Brent 0–2d $0 (n/a), post+48h $0 (n/a); https://x.com/ostium/status/2033512863537754504 — The Fed releases its economic projections and rate outlook this week, a moment that often resets expectations across global markets. The Forward Guidance Boost Window is live. Trade Gold, Oil, US500, US100 &amp; EUR/USD with double points …
- 2026-03-10 impressions 3,396; WTI 0–2d $88,997,121 (+288.9%), post+48h $100,369,487 (+301.6%); Brent 0–2d $0 (n/a), post+48h $0 (n/a); https://x.com/ostium/status/2031411333053428214 — $180M in Oil volume on Ostium last 24hrs. 498 unique traders. 3,294 trades. Largest single trade: $8M, Price impact: 4.31bps Will the volatility continue or is the war over? https://t.co/iRdgOIRIS0
- 2026-03-10 impressions 1,125; WTI 0–2d $88,997,121 (+288.9%), post+48h $100,361,280 (+301.5%); Brent 0–2d $0 (n/a), post+48h $0 (n/a); https://x.com/ostium/status/2031413050570617147 — Trade Oil on Ostium: https://t.co/9uZoci4yPF
- 2026-03-10 impressions 3; WTI 0–2d $88,997,121 (+288.9%), post+48h $40,913,316 (+41.0%); Brent 0–2d $0 (n/a), post+48h $0 (n/a); https://x.com/ostium/status/2031471566928978305 — RT @kaledora: oil and gold are the two top traded markets on @ostium - oil alone is 50% of our daily volume https://t.co/Rpa5pK4l7o

## Post-time robustness read
- 2026-03-02 impressions 3,382; WTI 0–2d +1545.7%; WTI 1–2d +2084.4%; WTI exact post+48h +1330.5%; WTI exact post+72h +1497.2%; https://x.com/ostium/status/2028297343775445238 — The world is watching the conflict unfold, and markets are responding in real time. The Fog of War Boost Window is live. Trade Oil, Gold, PLTR, CVX, and XOM with double points. This week only. https://t.co/CxHGq6s3L8
- 2026-03-09 impressions 3,477; WTI 0–2d +821.1%; WTI 1–2d +681.9%; WTI exact post+48h +898.9%; WTI exact post+72h +597.1%; https://x.com/ostium/status/2030992222892839275 — The Strait of Hormuz carries ~20% of global oil supply, and rising Iran tensions are putting supply chains under pressure. The Chokepoint Boost Window is live. Trade Oil, Silver, Gold, Copper &amp; USD/JPY with double points this week. htt…
- 2026-03-09 impressions 0; WTI 0–2d +821.1%; WTI 1–2d +681.9%; WTI exact post+48h +896.7%; WTI exact post+72h +597.0%; https://x.com/ostium/status/2031011633909432824 — RT @Copin_io: $5.6M Oil Trading Masterclass on @ostium! 🛢️ This wallet started trading $CL (crude oil) in late February and had alread…
- 2026-03-03 impressions 11,345; WTI 0–2d +1444.7%; WTI 1–2d +1209.2%; WTI exact post+48h +789.5%; WTI exact post+72h +628.0%; https://x.com/ostium/status/2028934137235558417 — One of the smart money traders on Ostium just rotated out of silver into crude oil. $774M volume on XAG. +$1.6M realized. Moved every dollar into CL longs $5M clips at a time. Currently sitting on ~$20M. Copy trade XAG, CL, and 200+ market…
- 2026-03-16 impressions 2,586; WTI 0–2d +245.4%; WTI 1–2d +408.6%; WTI exact post+48h +356.3%; WTI exact post+72h +260.9%; https://x.com/ostium/status/2033512863537754504 — The Fed releases its economic projections and rate outlook this week, a moment that often resets expectations across global markets. The Forward Guidance Boost Window is live. Trade Gold, Oil, US500, US100 &amp; EUR/USD with double points …
- 2026-03-17 impressions 4,416; WTI 0–2d +394.7%; WTI 1–2d +404.4%; WTI exact post+48h +335.4%; WTI exact post+72h +203.3%; https://x.com/ostium/status/2034034779063198173 — This smart money trader on Ostium just opened four $9.8M positions. $39.4M in oil at only 4.5 bps. The Strait of Hormuz is closed. Oil is still open to trade. https://t.co/701UpboL1c
- 2026-03-17 impressions 1,217; WTI 0–2d +394.7%; WTI 1–2d +404.4%; WTI exact post+48h +335.4%; WTI exact post+72h +203.3%; https://x.com/ostium/status/2034034791943967135 — Trade Oil on Ostium: https://t.co/9uZoci4yPF
- 2026-03-10 impressions 3,396; WTI 0–2d +288.9%; WTI 1–2d +62.5%; WTI exact post+48h +301.6%; WTI exact post+72h +175.3%; https://x.com/ostium/status/2031411333053428214 — $180M in Oil volume on Ostium last 24hrs. 498 unique traders. 3,294 trades. Largest single trade: $8M, Price impact: 4.31bps Will the volatility continue or is the war over? https://t.co/iRdgOIRIS0

## Highest social reach
- 2026-05-06 impressions 3,615,280; WTI range lift +27.4%; WTI activity lift -54.5%; https://x.com/ostium/status/2052072913566576963 — What the new liquidity engine means for you (the director's cut). Oil, gold, AI, and more. Try Ostium today.
- 2026-03-23 impressions 30,682; WTI range lift +33.3%; WTI activity lift -10.8%; https://x.com/ostium/status/2036180862891651128 — BRENT OIL LIVE NOW ON OSTIUM. https://t.co/GeERkR9T9j
- 2026-03-24 impressions 11,512; WTI range lift -19.8%; WTI activity lift -64.2%; https://x.com/ostium/status/2036488094296449322 — Ostium has no order books for a reason. Our traders today are sizing $2.5M+ positions across oil and gold, all at &lt;5bps spread. Access the most liquid global markets with the best execution onchain. https://t.co/L2qlGiuYbZ https://t.co/…
- 2026-03-03 impressions 11,345; WTI range lift +169.6%; WTI activity lift +1444.7%; https://x.com/ostium/status/2028934137235558417 — One of the smart money traders on Ostium just rotated out of silver into crude oil. $774M volume on XAG. +$1.6M realized. Moved every dollar into CL longs $5M clips at a time. Currently sitting on ~$20M. Copy trade XAG, CL, and 200+ market…
- 2026-04-03 impressions 10,028; WTI range lift -79.9%; WTI activity lift -99.9%; https://x.com/ostium/status/2040053134899204248 — Ostium in The Wall Street Journal. Trade oil, gold, and stocks onchain from the most liquid markets in the world. https://t.co/1F8WWV9tIW
- 2026-03-28 impressions 9,179; WTI range lift -58.4%; WTI activity lift -67.4%; https://x.com/ostium/status/2037929986305241286 — CL (WTI) is the benchmark for the US light oil market. Brent is the benchmark for the wider light oil market across Europe, Africa, and the Middle East. Trade both on Ostium. https://t.co/9aHzjMzOqU
- 2026-03-27 impressions 6,838; WTI range lift -39.9%; WTI activity lift -86.2%; https://x.com/ostium/status/2037640960159678503 — Another week of shipping what you asked for! 3 updates this week, straight from your feedback. Starting with: BRENT OIL ON OSTIUM... https://t.co/tti3rMhLpW
- 2026-03-05 impressions 5,795; WTI range lift +288.8%; WTI activity lift +150.1%; https://x.com/ostium/status/2029628328076800335 — Same trader closed the entire position Tuesday. Re-entered today. $14.5M in crude longs across 5 positions. Oil is the highest its been since June 2025. Iran struck a tanker yesterday. What do they know? https://t.co/AT2F2sMebr https://t.c…

## Readout

- v1.3 keeps the v1.2 calendar 0–2d primary window for continuity.
- Exact post-time activity windows test whether Ostium fills remained elevated after each social post went live.
- Calendar 1–2d is retained as an extra robustness layer, not as the main replacement window.
- 0–7d is retained only as context, because it can pick up unrelated market/protocol movements.
- This remains correlational: without competitor per-market volumes or randomized exposure, it cannot prove causality.

## Generated files

- `reports/ostium-oil-hormuz-event-study-v1_3.md`
- `reports/ostium-oil-hormuz-event-study-v1_3.csv`
- `data/processed/market_volatility_event_windows.csv`
- `data/processed/event_study_activity_windows.csv`
