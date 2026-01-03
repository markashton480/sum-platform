# Git Strategy

> **Single source of truth** for branch model, naming conventions, and merge rules.

This strategy is intentionally simple:

- **1 Version Declaration (VD) → 1 `release/<version>` or `infra/<initiative>` branch**
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
release/<version>                 Product releases (maps to VD, bumps sum-core)
infra/<initiative>                Infrastructure work (maps to VD, no version bump)
  ↑ PR (merge --no-ff)
feature/<work-order-slug>         Feature integration (maps to WO)
  ↑ PR (squash)
task/<task-slug>   or  fix/<task-slug>   Actual implementation work (maps to TASK/FIX)
```

### `release/*` vs `infra/*`

Both are top-level VD branches. The difference:

| Branch Type | When to Use | Version Bump? | Example |
|-------------|-------------|---------------|---------|
| `release/<version>` | Product features that ship in sum-core | Yes | `release/0.7.0` |
| `infra/<initiative>` | Tooling, themes, CI/CD, test harnesses | No | `infra/scale-infrastructure` |

**Use `release/*`** for work that:
- Adds features to sum-core
- Requires a new sum-core tag
- Is consumed by client projects via `pip install`

**Use `infra/*`** for work that:
- Improves development tooling (seeders, CLI)
- Updates themes or boilerplate
- Adds CI/CD or deployment infrastructure
- Doesn't change sum-core's public API

### Bypass branches (`docs/*`, `fix/*`)

Some branches bypass the normal hierarchy:

| Branch | When to use | Allowed targets |
|--------|-------------|-----------------|
| `docs/<slug>` | Documentation-only changes between releases | `develop`, `main`, or `release/*` |
| `fix/<slug>` | Hotfixes that can't wait for a release cycle | `develop`, `main`, or `release/*` |

**Requirements for bypass branches:**
- PR body must include a `## Bypass Justification` section explaining:
  - Why this can't go through the normal `task/*` → `feature/*` → `release/*` flow
  - Backport/forward-port plan if applicable

Example:
```bash
git checkout develop
git pull origin develop
git checkout -b docs/post-0.6.0-overhaul
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
| VD (product) | `release/<version>` | `release/0.6.0` |
| VD (infra) | `infra/<initiative-slug>` | `infra/scale-infrastructure` |
| WO | `feature/<work-order-slug>` | `feature/blog-upgrades` |
| TASK | `task/<task-slug>` | `task/add-category-filtering` |
| FIX | `fix/<task-slug>` | `fix/fix-the-fucking-blog` |
| *(bypass)* | `docs/<slug>` | `docs/post-0.6.0-overhaul` |

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
| `feature/*` → `release/*` or `infra/*` | **Merge `--no-ff`** | Preserve feature boundary in history |
| `release/*` → `develop` | **Squash** | One commit per version on `develop` |
| `infra/*` → `develop` | **Squash** | One commit per initiative on `develop` |
| `develop` → `main` | **Squash** | Clean production history |

---

## Workflow

### 1a) Start a product version (VD → `release/<version>`)

Create the Version Declaration issue first (see `VERSION_DECLARATION_TEMPLATE.md`). Then create the branch:

```bash
git checkout develop
git pull origin develop

git checkout -b release/0.7.0
git push -u origin release/0.7.0
```

### 1b) Start an infrastructure initiative (VD → `infra/<initiative>`)

For tooling, themes, CI/CD, or other non-product work:

```bash
git checkout develop
git pull origin develop

git checkout -b infra/scale-infrastructure
git push -u origin infra/scale-infrastructure
```

### 2) Start a work order (WO → `feature/<work-order-slug>`)

Feature branches come off the parent VD branch (`release/*` or `infra/*`):

```bash
git checkout release/0.7.0           # or infra/scale-infrastructure
git pull origin release/0.7.0

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
| `task/*` | `feature/<work-order-slug>` |
| `fix/*` *(in VD)* | `feature/<work-order-slug>` |
| `fix/*` *(bypass)* | `develop`, `main`, `release/*`, or `infra/*` |
| `docs/*` *(bypass)* | `develop`, `main`, `release/*`, or `infra/*` |
| `feature/*` | `release/<version>` or `infra/<initiative>` |
| `release/*` | `develop` |
| `infra/*` | `develop` |
| `develop` | `main` |

### 5) Finish a VD

**For product releases (`release/*`):**

1. Open PR `release/<version>` → `develop` (**squash**)
2. Then PR `develop` → `main` (**squash**)
3. Sync to `sum-core` and tag `v<version>`

**For infrastructure initiatives (`infra/*`):**

1. Open PR `infra/<initiative>` → `develop` (**squash**)
2. Then PR `develop` → `main` (**squash**)
3. No sum-core sync or tag (infra doesn't bump versions)

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
| Version Declaration (product) | `VD:` | `release/<version>` |
| Version Declaration (infra) | `VD:` | `infra/<initiative-slug>` |
| Work Order | `WO:` | `feature/<work-order-slug>` |
| Task | `TASK:` | `task/<task-slug>` |
| Fix | `FIX:` | `fix/<task-slug>` |

> **How to tell `release/*` vs `infra/*`:** The VD title indicates which. Product VDs use version numbers (e.g., `VD: v0.7.0 - Feature Name`). Infrastructure VDs use initiative names (e.g., `VD: Scale Infrastructure`).
