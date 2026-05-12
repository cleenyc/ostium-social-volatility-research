# Agent Runbook — Ostium Social Volatility Research Kit

Scope guard for this runbook:

- **Static dashboard:** local dashboard use only. Do not deploy or host unless separately approved.
- **Agent runbook and prompt templates:** make the workflow agent-runnable. Do not publish, create live jobs, or modify credentials.

## 1. Reproduce the cached oil/Hormuz study

From repo root:

```bash
npm install
npm run run:cached
npm run dashboard:data
npm run test
```

Expected cached headline counts:

- event-study posts: `29`
- unique post dates: `21`
- volatility-control rows: `101`
- high-volatility rows: `30`
- WTI eligible days: `75`
- Brent eligible days: `26`

## 2. Inspect the local dashboard

```bash
python3 -m http.server 8765 --directory dashboard
```

Open:

```text
http://127.0.0.1:8765/
```

Verify the dashboard includes:

- dashboard guard / scope chips;
- KPI cards;
- WTI/Brent high-volatility day control summaries;
- post-level event-study summaries;
- embedded report sections;
- configurable market-day explorer;
- local downloadable artifacts;
- searchable post-level drilldown;
- top social and WTI activity tables;
- limitation/caveat language.

## 3. Run validation before interpreting results

```bash
npm run validate
```

A clean cached oil/Hormuz run should report validation success. If validation fails, do not interpret the dashboard as current. Fix or regenerate the cached artifacts first.

## 4. Adapt to another market/topic

Copy the config:

```bash
cp configs/study.oil-hormuz.example.yaml configs/study.<topic>.example.yaml
```

Update:

- `study.id`, `study.title`, `study.description`, `start_time`, `end_time`;
- `social.x.query`;
- `classification.include_terms` and `classification.categories`;
- `markets[].label`, `ostium_builder_symbol`, `ostium_pair_id`, `display_name`;
- all output paths under `paths.raw`, `paths.processed`, and `paths.reports`;
- `validation.fixture_expectations` only after a baseline run confirms counts.

Then run the lower-level collection scripts only if the user has approved and configured source access:

```bash
node scripts/collect_event_study_activity_windows.mjs --study configs/study.<topic>.example.yaml
node scripts/collect_volatility_control_activity_windows.mjs --study configs/study.<topic>.example.yaml
```

Regenerate reports/dashboard:

```bash
PYTHONPATH=src python3 -m ostium_social_volatility report --study configs/study.<topic>.example.yaml
PYTHONPATH=src python3 scripts/build_dashboard_data.py --study configs/study.<topic>.example.yaml --out-dir dashboard/data
```

## 5. Required access for new/live studies

A new live study requires:

- X/Twitter full-archive search or equivalent historical export;
- Ostium Builder API OHLC data for target markets;
- Ostium SDK fills for target pair IDs;
- Node dependencies for collector scripts;
- Python environment for report/dashboard generation;
- public-output review if the result will be shared.

Do not print or commit credentials.

## 6. Interpretation checklist

When summarizing results, answer separately:

1. Did the account post about the topic?
2. Were the posts socially meaningful?
3. Was the market volatile around those posts?
4. Did Ostium pair-specific activity rise around those posts?
5. On high-volatility days, were post days different from no-post days?

Use cautious language:

- “aligned with”
- “coincided with”
- “directional relationship”
- “correlational, not causal”

Avoid unsupported language:

- “caused”
- “proved impact”
- “guaranteed repeatability”
- “recommendation engine” unless live monitoring/recommendations are explicitly approved

## 7. Scope boundaries

Allowed in this static research kit:

- local dashboard improvements;
- repo-local SKILL.md;
- runbook and prompt templates;
- local reproducibility docs;
- tests and validation.

Not allowed without explicit approval:

- public GitHub repo creation/push;
- Vercel/GitHub Pages/Cloudflare deployment;
- recurring cron/live monitor;
- external posting/messaging;
- credential changes;
- live recommendation engine.
