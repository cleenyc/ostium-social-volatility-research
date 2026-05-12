# Ostium Oil/Hormuz V1.2 Post-Time Scratch Check

Date: 2026-05-12

Purpose: preserve a no-code-change scratch comparison that tests whether the v1.2 activity lifts persist after excluding fills before the social post went out.

## Context

The v1.2 primary activity window is `0–2d`: calendar day of post plus the next two calendar days. This starts at `00:00 UTC` on the post date, so for afternoon/evening posts it can include fills that occurred before the post.

Chris's concern: if activity was already elevated earlier that day, a post may be reporting or reacting to activity rather than preceding it.

## Scratch method

No repo code was changed. A temporary script was run from:

- `/tmp/ostium_scratch_compare_windows.mjs`

The script used existing post data and the Ostium SDK to compare:

- Existing `0–2d`: calendar post day + next 2 days from the v1.2 report.
- Calendar `1–2d`: next day + day after only, excluding the post calendar day.
- Exact `48h after post`: fills from the tweet timestamp through 48 hours later.
- Exact `72h after post`: fills from the tweet timestamp through 72 hours later.
- Baseline: exact 30 days before the tweet timestamp.

This scratch check focuses on Ostium fill/activity data. Market-volatility data is daily OHLC, so it is not suitable for exact post-time slicing without intraday market data.

## Focus WTI results

### 2026-03-09 — Hormuz/chokepoint post

Post time: `13:00 UTC`

- Existing `0–2d` lift: `+821.1%`
- Calendar `1–2d` lift: `+588.4%`
- Exact `48h after post` lift: `+898.9%`
- Exact `72h after post` lift: `+597.1%`

Read: strongest and cleanest case. The lift persists after removing pre-post same-day fills, and exact 48h is even stronger than the original calendar window.

### 2026-03-03 — crude rotation post

Post time: `20:42 UTC`

- Existing `0–2d` lift: `+1444.7%`
- Calendar `1–2d` lift: `+720.4%`
- Exact `48h after post` lift: `+789.5%`
- Exact `72h after post` lift: `+628.0%`

Read: still a strong after-post activity signal.

### 2026-03-10 — `$180M oil volume` post

Post time: `16:46 UTC`

- Existing `0–2d` lift: `+288.9%`
- Calendar `1–2d` lift: `+48.7%`
- Exact `48h after post` lift: `+301.6%`
- Exact `72h after post` lift: `+175.3%`

Read: mixed. Exact post-time remains strong, but next-calendar-days-only weakens sharply. This may reflect an already-active oil regime and/or intraday timing effects.

### 2026-03-17 — `$39.4M oil / Hormuz` post

Post time: `22:30 UTC`

- Existing `0–2d` lift: `+394.7%`
- Calendar `1–2d` lift: `+335.4%`
- Exact `48h after post` lift: `+335.4%`
- Exact `72h after post` lift: `+203.3%`

Read: strong after-post activity persists, though the market-volatility alignment in the main v1.2 report was weaker than March 9 or March 3.

### 2026-03-05 — tanker / crude longs post

Post time: `18:41 UTC`

- Existing `0–2d` lift: `+150.1%`
- Calendar `1–2d` lift: `+41.7%`
- Exact `48h after post` lift: `+51.9%`
- Exact `72h after post` lift: `+1.3%`

Read: positive but much less compelling after isolating post-time effects.

## Takeaway

The after-post scratch check supports the main v1.2 read for the strongest cases:

1. March 9 remains the cleanest all-signals case.
2. March 3 remains a strong after-post activity-lift case.
3. March 17 remains strong for after-post activity, though less strong on market-volatility alignment.
4. March 10 is interesting but more ambiguous.
5. March 5 weakens materially when pre-post same-day activity is excluded.

## Suggested future formalization

If this becomes v1.3, formalize a post-time-aware activity analysis with this direction:

- Keep existing calendar `0–2d` as the main primary window.
- Add exact `post_time → +48h` and/or `post_time → +72h` activity windows because they directly test whether fills increased after the social post went live.
- Add after-post-only lift columns for WTI and Brent, so each event can show both current calendar-window lift and exact post-time lift.
- Update report rankings to account for whether each case remains strong after the post-time check.
- Keep calendar `1–2d` as an optional extra robustness layer, not the main replacement window.
- Keep market OHLC volatility on daily windows unless intraday WTI/Brent data is added.
