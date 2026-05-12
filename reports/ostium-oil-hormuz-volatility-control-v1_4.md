# Ostium Oil/Hormuz V1.4 Volatility-Day Control Report

Date: 2026-05-12

## Method

- Question: on high oil-volatility days, was Ostium activity higher when Ostium posted oil content than when it did not?
- Markets: WTI over all available WTI OHLC days; Brent over all available Brent OHLC days.
- Eligible market days require at least 10 prior OHLC observations in the 30-day rolling baseline.
- High-volatility definition: daily range lift > 0 and daily range percentile vs rolling baseline >= 75th percentile.
- Post flag: date has at least one oil/Hormuz-related `@Ostium` post from the v1.3 event table.
- Activity outcome: Ostium SDK notional/day in the calendar `0–2d` window vs the prior 30-day activity baseline.
- This is a control comparison, not causal proof; oil posts are not randomized and may be triggered by the same volatility that drives trading.

## Coverage

- Oil posts available: 29 posts across 21 dates.
- Raw activity windows collected: 242.
- WTI: 75 eligible market days (2026-02-12 to 2026-05-11); high-volatility days: 25.
- BRENT: 26 eligible market days (2026-04-06 to 2026-05-11); high-volatility days: 5.

## High-volatility post vs no-post comparison

### WTI

- High-volatility days with oil post: 10; without oil post: 15.
- Median activity lift with oil post: +74.0%; without oil post: -9.3%.
- Mean activity lift with oil post: +402.2%; without oil post: +105.0%.
- Positive activity-lift days with oil post: 5/10; without oil post: 6/15.
- Median event notional/day with oil post: $35,939,253; without oil post: $6,517,662.

### BRENT

- High-volatility days with oil post: 1; without oil post: 4.
- Median activity lift with oil post: -75.1%; without oil post: -98.6%.
- Mean activity lift with oil post: -75.1%; without oil post: -94.3%.
- Positive activity-lift days with oil post: 0/1; without oil post: 0/4.
- Median event notional/day with oil post: $1,409,731; without oil post: $221,691.

## Highest-volatility days

### WTI
- 2026-03-09 [post]; range 34.0% vs baseline 4.0% (+755.8%); activity lift +821.1%; notional/day $150,586,882; oil posts 2.
- 2026-03-06 [no post]; range 16.8% vs baseline 3.4% (+393.1%); activity lift +103.1%; notional/day $28,018,503; oil posts 0.
- 2026-03-03 [post]; range 9.5% vs baseline 2.9% (+231.4%); activity lift +1444.7%; notional/day $86,143,365; oil posts 1.
- 2026-03-10 [post]; range 15.2% vs baseline 5.1% (+197.1%); activity lift +288.9%; notional/day $88,997,121; oil posts 3.
- 2026-03-11 [post]; range 15.0% vs baseline 5.7% (+164.5%); activity lift -2.0%; notional/day $28,707,717; oil posts 1.
- 2026-03-05 [post]; range 8.6% vs baseline 3.3% (+163.4%); activity lift +150.1%; notional/day $30,818,758; oil posts 1.
- 2026-04-07 [no post]; range 19.9% vs baseline 8.5% (+133.6%); activity lift +31.3%; notional/day $62,031,356; oil posts 0.
- 2026-03-23 [post]; range 17.3% vs baseline 7.6% (+127.9%); activity lift -10.8%; notional/day $41,059,748; oil posts 1.
- 2026-02-18 [no post]; range 5.3% vs baseline 2.7% (+99.4%); activity lift -11.0%; notional/day $5,690,361; oil posts 0.
- 2026-05-06 [post]; range 12.0% vs baseline 6.1% (+97.3%); activity lift -54.5%; notional/day $4,091,975; oil posts 2.

### BRENT
- 2026-05-06 [post]; range 11.2% vs baseline 5.4% (+106.7%); activity lift -75.1%; notional/day $1,409,731; oil posts 2.
- 2026-04-17 [no post]; range 11.4% vs baseline 5.6% (+102.7%); activity lift -99.3%; notional/day $124,392; oil posts 0.
- 2026-04-29 [no post]; range 8.2% vs baseline 5.5% (+49.2%); activity lift -98.5%; notional/day $206,128; oil posts 0.
- 2026-05-04 [no post]; range 7.8% vs baseline 5.4% (+44.4%); activity lift -80.9%; notional/day $1,075,029; oil posts 0.
- 2026-04-21 [no post]; range 7.2% vs baseline 5.9% (+22.3%); activity lift -98.7%; notional/day $237,254; oil posts 0.

## Correlation checks

- WTI: range-lift vs activity-lift correlation across eligible days: 0.46 (n=75); across high-volatility days: 0.33 (n=25).
- BRENT: range-lift vs activity-lift correlation across eligible days: -0.19 (n=26); across high-volatility days: 0.34 (n=5).

## Readout

- V1.4 adds the missing control group: high-volatility days with no oil post.
- Interpret median/positive-day differences as directional evidence only, because post timing is endogenous to market volatility and campaign decisions.
- If high-volatility post days show materially higher activity than no-post days, that supports the thesis that posting may amplify activity beyond volatility alone.

## Generated files

- `reports/ostium-oil-hormuz-volatility-control-v1_4.md`
- `reports/ostium-oil-hormuz-volatility-control-v1_4.csv`
- `data/processed/volatility_control_days.csv`
