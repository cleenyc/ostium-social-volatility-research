# Prompt Template — Reproduce Cached Study

You are running the Ostium Social Volatility Research Kit.

Phase scope:

- Phase 3: local dashboard only; do not deploy.
- Phase 4: use repo-local skill/runbook; do not publish or create live jobs.

Tasks:

1. Read `SKILL.md`, `docs/agent-runbook.md`, and `configs/study.oil-hormuz.example.yaml`.
2. Run:
   ```bash
   npm install
   npm run run:cached
   npm run dashboard:data
   npm run test
   ```
3. Verify the expected cached counts:
   - 29 posts
   - 21 unique dates
   - 101 volatility-control rows
   - 30 high-volatility rows
   - WTI 75 eligible days
   - Brent 26 eligible days
4. Inspect `dashboard/data/summary.json` and summarize:
   - WTI high-vol post vs no-post activity lift;
   - Brent caveat;
   - dashboard artifacts generated;
   - any validation warnings/failures.
5. Use correlational language only. Do not claim causality.
