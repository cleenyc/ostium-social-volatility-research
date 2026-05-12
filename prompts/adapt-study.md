# Prompt Template — Adapt Study Target

You are adapting the Ostium Social Volatility Research Kit to a new target market/topic.

Phase scope:

- Phase 3: keep dashboard work local/static.
- Phase 4: create config/runbook updates only.
- Do not deploy, publish, modify credentials, create recurring jobs, or start live monitoring.

Inputs from user:

- target topic/query terms;
- target market(s);
- Ostium Builder symbol(s);
- Ostium pair ID(s);
- date range;
- available X/Twitter access path (`xurl`, raw X API, or supplied export).

Tasks:

1. Read `SKILL.md`, `docs/agent-runbook.md`, `docs/adapt-study.md`, and `configs/study.oil-hormuz.example.yaml`.
2. Create `configs/study.<target>.example.yaml` without overwriting the oil/Hormuz fixture.
3. Update study, social, classification, markets, paths, and validation fields.
4. If source access is approved and configured, run collectors:
   ```bash
   node scripts/collect_event_study_activity_windows.mjs --study configs/study.<target>.example.yaml
   node scripts/collect_volatility_control_activity_windows.mjs --study configs/study.<target>.example.yaml
   ```
5. Regenerate reports/dashboard:
   ```bash
   PYTHONPATH=src python3 -m ostium_social_volatility report --study configs/study.<target>.example.yaml
   PYTHONPATH=src python3 scripts/build_dashboard_data.py --study configs/study.<target>.example.yaml --out-dir dashboard/data
   ```
6. Run validation/tests and summarize results with caveats.

Output:

- files changed;
- commands run;
- validation/test results;
- interpretation limits;
- whether any approval-gated step remains.
