## A lightweight branching / commit strategy


* Use `main` as the stable branch.
* For each task ticket (e.g. `M0-001`), create a feature branch:

  * `git checkout -b feat/m0-001-monorepo-tooling`
* Commit in small slices:

  * `chore:` for tooling/infra
  * `feat:` for new functionality
  * `fix:` for bug fixes
* Merge back into `main` once the ticket is “done” and tests pass.

We can tighten this into a more formal flow (branch protection, required checks, etc.) later.

| Type | Pattern | Example |
|------|---------|---------|
| Feature | `feature:<scope>-<description>` | `feature:blocks-testimonial-carousel` |
| Bug Fix | `fix:<scope>-<description>` | `fix:leads-email-notification` |
| Hotfix | `hotfix:<description>` | `hotfix:xss-vulnerability` |
| Chore | `chore:<description>` | `chore:update-wagtail-7.1` |
| Documentation | `docs:<description>` | `docs:deployment-guide` |
| Refactor | `refactor:<scope>-<description>` | `refactorblocks-base-class` |