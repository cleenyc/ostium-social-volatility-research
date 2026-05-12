# Publication Checklist

Use this checklist before pushing, publishing, or deploying a fork of the research kit.

## Scope guard

- [ ] Public packaging only: no live monitor, recommendation engine, recurring job, or external posting.
- [ ] Dashboard hosting is static-only unless a separate live/backend review has been approved.
- [ ] `run --mode live` remains disabled or clearly guarded until credential/source behavior is explicit.

## Secret and environment review

- [ ] No `.env`, `.env.*`, `.xurl`, OAuth files, auth directories, token files, or local Hermes config files.
- [ ] No hardcoded API keys, bearer tokens, passwords, private keys, or credential-bearing logs.
- [ ] No local absolute paths in public instructions or generated outputs.
- [ ] Example configs use placeholders or public-safe fixture paths only.

Suggested checks:

```bash
git ls-files | grep -Ei '(\.env|\.xurl|token|secret|credential|oauth|auth)'
git grep -nEi 'api[_-]?key|bearer |password|client_secret|private[_-]?key|github_token|anthropic|openai|/opt/data|/root|HERMES_HOME'
```

Review matches manually: docs may mention forbidden file names as examples, but no real secrets should appear.

## Data/source review

- [ ] Social data shown publicly is intended to be public-facing and points back to public X post URLs where practical.
- [ ] Public dashboard/report does not include private account auth artifacts or private user data.
- [ ] Ostium activity artifacts are reproducibility fixtures, not credentialed account exports.
- [ ] Market OHLC files are either redistributable fixtures or clearly replaceable by user-provided files.

## Reproducibility review

- [ ] `npm install` succeeds.
- [ ] `npm run run:cached` succeeds.
- [ ] `npm run dashboard:data` succeeds.
- [ ] `npm run test` succeeds.
- [ ] `dashboard/` renders locally with `python -m http.server 8765 --directory dashboard`.

## Public repo settings

Recommended GitHub settings:

- Public repository with issues enabled.
- Default branch: `main`.
- Optional: add GitHub Actions CI later if publishing with a token that has workflow scope.
- Pages or static host points to `dashboard/` only if/when dashboard publication is desired.
- No repository secrets are required for cached reproduction.
