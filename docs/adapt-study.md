# Adaptation Guide — Changing the Study Target

Phase guard:

- **Phase 3:** dashboard should support local/static exploration of cached/generated outputs.
- **Phase 4:** this guide makes the study configurable and agent-runnable.
- Do not deploy, publish, create live jobs, or modify credentials while using this guide.

This guide explains how to adapt the oil/Hormuz fixture to another market/topic without rewriting the code.

## Example target choices

Suitable targets have:

- a social topic/query that can be collected historically;
- one or more Ostium-supported markets;
- known Builder API symbols and Ostium pair IDs;
- enough market/activity history for a baseline and event window.

Examples could include another commodity, FX pair, index, crypto market, or macro theme, provided the data access exists.

## Config fields to change

Start with:

```bash
cp configs/study.oil-hormuz.example.yaml configs/study.<target>.example.yaml
```

### `study`

Change:

```yaml
study:
  id: <target_id>
  title: "<Readable Study Title>"
  description: "Analyze whether <account/topic> posts align with <market> volatility and Ostium activity."
  start_time: "YYYY-MM-DDT00:00:00Z"
  end_time: "YYYY-MM-DDT23:59:59Z"
```

### `social.x.query`

Change the query and required access notes:

```yaml
social:
  x:
    query: "from:<account> <topic terms>"
```

Historical studies need full-archive search or an equivalent export. Recent search is not enough for a historical backtest.

### `classification.include_terms`

Define topic terms and categories:

```yaml
classification:
  include_terms:
    - <topic>
    - <synonym>
  categories:
    <topic>:
      - <topic>
      - <synonym>
```

Categories drive filtering and dashboard labels. Keep them specific enough to avoid unrelated posts.

### `markets`

For each market:

```yaml
markets:
  - label: <SHORT_LABEL>
    ostium_builder_symbol: "<SYMBOL>"
    ostium_pair_id: <PAIR_ID>
    display_name: "<Readable Name>"
    include_in_headline: true
```

Verify pair IDs and symbols before running collectors.

### `windows`

Default methodology:

- 30-day baseline;
- primary `0-2d` calendar event window;
- `1-2d`, `+48h`, and `+72h` robustness/context views.

Do not change the primary window unless the research question requires it. If changed, document why in the report and dashboard copy.

### `paths`

Write new outputs to target-specific paths so the oil/Hormuz fixture remains reproducible:

```yaml
paths:
  raw:
    x_posts: "data/raw/social/x_<target>.json"
  processed:
    posts: "data/processed/<target>_posts.csv"
  reports:
    event_study_md: "reports/<target>-event-study-v1_3.md"
    event_study_csv: "reports/<target>-event-study-v1_3.csv"
    volatility_control_md: "reports/<target>-volatility-control-v1_4.md"
    volatility_control_csv: "reports/<target>-volatility-control-v1_4.csv"
```

### `validation.fixture_expectations`

For first exploratory runs, remove fixture-specific exact counts. After producing a known-good baseline, add expectations to lock reproducibility.

## Agent prompt for adaptation

Use `prompts/adapt-study.md` as the starting instruction for an agent.

The agent should:

1. clone/open the repo;
2. inspect `configs/study.oil-hormuz.example.yaml`;
3. create a target config;
4. verify source access and pair IDs;
5. run collectors only if approved;
6. regenerate reports and dashboard;
7. run tests/validation;
8. summarize results cautiously.

## Public-output review

Before Phase 5 public packaging, review:

- raw X fixture contents;
- full tweet text exposure;
- credential/token files;
- local absolute paths;
- private Chris/Hermes context;
- data-source terms/caveats.
