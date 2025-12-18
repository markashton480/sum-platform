## Git strategy (develop-based integration)

### Branch model

* `main` is the **stable** branch.
  * Only receives changes via PRs from `develop` (release promotion).
* `develop` is the **integration** branch.
  * All work branches are cut from `develop`.
  * Work lands back into `develop` via PR.

### Day-to-day workflow

1. Update local `develop`:

   * `git checkout develop`
   * `git pull`

2. Create a ticket branch from `develop`:

   * `feat/<ticket>-<short-slug>`
   * `fix/<ticket>-<short-slug>`
   * `chore/<ticket>-<short-slug>`
   * `docs/<ticket>-<short-slug>`
   * `cm/<ticket>-<short-slug>`

   Example:
   * `git checkout -b feat/CM-M6-QA-08-develop-workflow`

3. Open a PR **into `develop`**.
  * Recommended for code changes.
  * CI (`lint-and-test`) will run, but `develop` does not enforce checks.

### Releases (promotion to main)

* When `develop` is in a releasable state, open a PR: `develop`  `main`.
* CI must pass; merge via your chosen merge strategy.

### Hotfixes

* If production needs an emergency fix:
  1. Branch from `main`, open PR back into `main`.
  2. Backport the same change into `develop` (PR into `develop`).

### Notes on protections

* `main` is protected and should only receive changes via PR (typically `develop` → `main`).
* `develop` is intentionally **unprotected** to allow direct pushes (e.g. CM tickets, transcripts, work reports).
  * CI may still run on `develop` for visibility, but it is not a merge/push gate.

| Type | Pattern | Example |
|------|---------|---------|
| Feature | `feature:<scope>-<description>` | `feature:blocks-testimonial-carousel` |
| Bug Fix | `fix:<scope>-<description>` | `fix:leads-email-notification` |
| Hotfix | `hotfix:<description>` | `hotfix:xss-vulnerability` |
| Chore | `chore:<description>` | `chore:update-wagtail-7.1` |
| Documentation | `docs:<description>` | `docs:deployment-guide` |
| Refactor | `refactor:<scope>-<description>` | `refactor:blocks-base-class` |