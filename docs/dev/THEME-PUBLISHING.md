# Theme Publishing Workflow

Theme sources live in `sum-platform/themes/` and are published to the
distribution repo `sum-themes` when you are ready to ship updates.

## Script: `scripts/publish_themes.py`

This script copies `themes/*` into the `sum-themes` repo, commits the changes,
and pushes to the `main` branch. It does not run any build steps; compiled
assets in each theme directory are preserved as-is.

### Requirements

- Git access to `markashton480/sum-themes`
- Clean working tree in `sum-platform`

### Usage

Dry run (no commit or push):

```bash
python scripts/publish_themes.py --dry-run
```

Publish to the default repo:

```bash
python scripts/publish_themes.py
```

Publish using a custom clone path:

```bash
python scripts/publish_themes.py --themes-repo-path /tmp/sum-themes-sync
```

### Notes

- Default repo URL: `git@github.com:markashton480/sum-themes.git`
- Target branch: `main`
- Commit message includes the source SHA and list of themes
