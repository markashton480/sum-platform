# Git Strategy

> **Single source of truth** for branch model, naming conventions, and merge rules.

This strategy is intentionally simple:

- **1 Version Declaration (VD) → 1 `release/<version>` branch**
- **1 Work Order (WO) → 1 `feature/<work-order-slug>` branch**
- **1 Task Ticket (TASK/FIX) → 1 `task/*` or `fix/*` branch**

## Repository Model

SUM Platform uses a **two-repository model**:

| Repository | Visibility | Purpose |
|------------|------------|---------|
| `sum-platform` | Private | Development monorepo |
| `sum-core` | Public | Distribution repo for `pip install` |

Releases sync from `sum-platform` → `sum-core`. Tags are created on `sum-core` because that’s what client projects reference.

---

## Branch Model

```
main                              Production, tagged releases
  ↑ PR (squash)
develop                           Stable integration, always deployable
  ↑ PR (squash)
release/<version>                 Version integration (maps to VD)
  ↑ PR (merge --no-ff)
feature/<work-order-slug>         Feature integration (maps to WO)
  ↑ PR (squash)
task/<task-slug>   or  fix/<task-slug>   Actual implementation work (maps to TASK/FIX)
```

### Why tasks are NOT nested under `feature/<...>/...`

Git **cannot** have both:

- `feature/blog-upgrades` **and**
- `feature/blog-upgrades/some-task`

because refs behave like file paths (a branch is a file under `refs/heads/`).

That’s why task branches use `task/*` or `fix/*`.

---

## Naming Conventions

### Branch names

**No trailing slash.** Git branch names cannot end with `/`.

| Issue Level | Branch Pattern | Example |
|------------|----------------|---------|
| VD | `release/<version>` | `release/0.6.0` |
| WO | `feature/<work-order-slug>` | `feature/blog-upgrades` |
| TASK | `task/<task-slug>` | `task/add-category-filtering` |
| FIX | `fix/<task-slug>` | `fix/fix-the-fucking-blog` |

### Slug rules

Use the issue title text (after the prefix like `WO:` / `TASK:` / `FIX:`) and convert it to a slug:

- lower-case
- spaces → `-`
- remove punctuation (keep letters/numbers/hyphens)
- collapse multiple `-`
- trim leading/trailing `-`

Examples:

- `WO: Blog Upgrades` → `feature/blog-upgrades`
- `TASK: Add category filtering` → `task/add-category-filtering`
- `FIX: Fix the fucking blog` → `fix/fix-the-fucking-blog`

> If you ever hit a collision (rare), append a short disambiguator: `task/<slug>-2` or `task/<slug>-gh123`.

---

## Merge Strategy

| From → To | Strategy | Rationale |
|----------|----------|-----------|
| `task/*` or `fix/*` → `feature/*` | **Squash** | Clean feature history, one commit per task |
| `feature/*` → `release/*` | **Merge `--no-ff`** | Preserve feature boundary in history |
| `release/*` → `develop` | **Squash** | One commit per version on `develop`. |
| `develop` → `main` | **Squash** | Clean production history |

---

## Workflow

### 1) Start a version (VD → `release/<version>`)

Create the Version Declaration issue first (see `VERSION_DECLARATION_TEMPLATE.md`). Then create the branch:

```bash
git checkout develop
git pull origin develop

git checkout -b release/0.6.0
git push -u origin release/0.6.0
```

### 2) Start a work order (WO → `feature/<work-order-slug>`)

Feature branches always come off the release branch:

```bash
git checkout release/0.6.0
git pull origin release/0.6.0

git checkout -b feature/blog-upgrades
git push -u origin feature/blog-upgrades
```

> If you don’t pre-create feature branches, the **first task under the WO** may create it (the GH-ISSUE prompt supports this).

### 3) Start a task or fix (TASK/FIX → `task/*` or `fix/*`)

Task/fix branches always come off the feature branch:

```bash
git checkout feature/blog-upgrades
git pull origin feature/blog-upgrades

git checkout -b task/fix-the-fucking-blog
git push -u origin task/fix-the-fucking-blog
```

### 4) PR targeting rules

| Your Branch | PR Target |
|------------|-----------|
| `task/*` or `fix/*` | `feature/<work-order-slug>` |
| `feature/*` | `release/<version>` |
| `release/*` | `develop` |
| `develop` | `main` |

### 5) Finish a version

When all WOs are merged into the release branch:

1. Open PR `release/<version>` → `develop` (**squash**)
2. Then PR `develop` → `main` (**squash**)
3. Sync to `sum-core` and tag `v<version>`

---

## Commit messages

Use Conventional Commits:

```
<type>(<optional-scope>): <description>

Closes #<issue-number>
```

Types: `feat`, `fix`, `chore`, `docs`, `refactor`, `test`

---

## Issue ↔ Branch mapping

| Issue Type | Title Prefix | Branch |
|-----------|--------------|--------|
| Version Declaration | `VD:` | `release/<version>` |
| Work Order | `WO:` | `feature/<work-order-slug>` |
| Task | `TASK:` | `task/<task-slug>` |
| Fix | `FIX:` | `fix/<task-slug>` |
