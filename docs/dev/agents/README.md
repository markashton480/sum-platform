# Codex prompts and SUM preflight

This repo ships a Codex prompt template and a small preflight helper to keep feature branches aligned with `origin/develop` before work starts.

## Installing the prompt

Codex CLI looks for custom prompts in `~/.codex/prompts/` and exposes them via `/prompts:<name>`.

```bash
mkdir -p ~/.codex/prompts
cp docs/dev/codex/prompts/sum-preflight.md ~/.codex/prompts/sum-preflight.md
```

Restart your Codex session after copying so it reloads prompts.

## Using the prompt

Invoke the prompt at the start of any ticket to run the repo preflight:

```
/prompts:sum-preflight TICKET_ID=THEME-0XX
```

The prompt runs `make preflight`, shows the diff, and prints a reminder about generated theme assets.

## Preflight script

`make preflight` wraps `scripts/codex_preflight.sh`, which:
- Refuses to run on a dirty working tree (prompts you to commit/stash)
- Fetches `origin` and ensures `origin/develop` exists
- Detects relationship to `origin/develop`; rebases if behind, stops if diverged
- Prints next steps: run tests, rebuild theme CSS/fingerprint if you changed inputs, and regenerate rather than hand-merge generated assets

Treat `docs/dev/codex/prompts/sum-preflight.md` as the canonical template; local copies in `~/.codex/prompts/` are untracked and per-user.
