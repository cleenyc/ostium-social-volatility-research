# Prompt Template — Interpret Results

You are interpreting outputs from the Ostium Social Volatility Research Kit.

Phase scope:

- Phase 3: use the local/static dashboard outputs only.
- Phase 4: use repo-local skill/runbook guidance.
- Do not deploy or publish any outputs from this interpretation task.

Read first:

- `SKILL.md`
- `docs/agent-runbook.md`
- `docs/adapt-study.md`
- `prompts/reproduce-cached-study.md`
- `prompts/adapt-study.md`
- `prompts/interpret-results.md`

Do not deploy or publish any outputs from this interpretation task.

Answer these questions separately:

1. Did the account post about the target topic?
2. Were those posts socially meaningful?
3. Was the market volatile around those posts?
4. Did Ostium market-specific activity rise around those posts?
5. On high-volatility market days, were post days different from no-post days?

Required language:

- “aligned with”
- “coincided with”
- “directional relationship”
- “correlational, not causal”

Avoid:

- “caused”
- “proved”
- “guaranteed”
- “recommendation engine” unless Phase 6 has been explicitly approved

For the oil/Hormuz fixture, preserve the headline caveats:

- WTI is directionally positive in the v1.4 control comparison.
- Brent is underpowered and inconclusive.
- Social reach and trading activity are separate outcomes.
- Same-day or adjacent posts can share windows.
