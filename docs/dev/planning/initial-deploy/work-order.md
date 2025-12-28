# Work Order

**Title:** `WO: Initial Sage & Stone Deployment (v0.6.0)`

---

## Parent

**Version Declaration:** #190 (v0.6.0)

---

## Branch

| Branch                  | Target          |
| ----------------------- | --------------- |
| `feature/initial-deploy` | `release/0.6.0` |

```bash
git checkout release/0.6.0
git checkout -b feature/initial-deploy
git push -u origin feature/initial-deploy
```

---

## Objective

- [ ] Consolidate and organize deployment documentation into `/infrastructure/`
- [ ] Establish SSH key strategy and secrets management approach
- [ ] Provision first VPS (sandbox/staging environment)
- [ ] Deploy Sage & Stone site to `sage-and-stone.lintel.site`
- [ ] Complete smoke tests and update operational tracking
- [ ] Document lessons learned in `what-broke-last-time.md`

---

## Scope

### In Scope

- Documentation consolidation: move `docs/dev/deploy/vps-golden-path.md` to `/infrastructure/docs/`
- Remove empty `docs/dev/deploy/` directory
- SSH key strategy documentation for deploy user access
- VPS provisioning using `provision_vps.sh` and golden path
- First Sage & Stone deployment to staging domain
- Smoke tests per `smoke-tests.md`
- Loop sites matrix update

### Out of Scope

- Production domain setup (uses staging `*.lintel.site` only)
- Automated CI/CD pipeline (manual deploy for M6)
- Celery worker setup (optional, not required for launch)
- Multi-site VPS hosting (single site for initial validation)
- External monitoring setup (future scope)

---

## Subtasks

| #   | Issue                                           | Branch                               | Status |
| --- | ----------------------------------------------- | ------------------------------------ | ------ |
| 1   | #XXX: Consolidate deployment documentation      | `feature/initial-deploy/001-docs`    | 🔲     |
| 2   | #YYY: Document SSH key strategy                 | `feature/initial-deploy/002-ssh`     | 🔲     |
| 3   | #ZZZ: Provision staging VPS                     | (manual ops - no branch)             | 🔲     |
| 4   | #AAA: Deploy Sage & Stone to staging            | (manual ops - no branch)             | 🔲     |
| 5   | #BBB: Execute smoke tests and update tracking   | (manual ops - no branch)             | 🔲     |

**Status:** 🔲 Todo | 🔄 In Progress | ✅ Done

---

## Merge Plan

### Order

```
┌─────────────────────────────────────────────────┐
│              MERGE DEPENDENCY GRAPH              │
├─────────────────────────────────────────────────┤
│                                                 │
│   #1 Consolidate Docs ─┐                        │
│                        ├──► PR to release/0.6.0 │
│   #2 SSH Key Strategy ─┘                        │
│                                                 │
│   #3 Provision VPS (ops, no merge)              │
│        │                                        │
│        ▼                                        │
│   #4 Deploy Sage & Stone (ops, no merge)        │
│        │                                        │
│        ▼                                        │
│   #5 Smoke Tests + Tracking (ops, no merge)     │
│                                                 │
└─────────────────────────────────────────────────┘
```

1. **#1 + #2** — Can run in parallel; both are documentation
2. **#3** — Requires SSH strategy defined; VPS provisioned manually
3. **#4** — Requires VPS ready; executes deploy.sh
4. **#5** — Requires deployment complete; validates and records

### Hot Files

| File                                      | Owner | Notes                          |
| ----------------------------------------- | ----- | ------------------------------ |
| `infrastructure/docs/vps-golden-path.md`  | #1    | Moved from docs/dev/deploy/    |
| `infrastructure/docs/ssh-strategy.md`     | #2    | New file                       |
| `docs/ops-pack/loop-sites-matrix.md`      | #5    | Updated with Sage & Stone      |

---

## Affected Paths

```
infrastructure/
├── docs/
│   ├── vps-golden-path.md      # Moved
│   └── ssh-strategy.md         # New
├── scripts/                    # Existing (unchanged)
├── systemd/                    # Existing (unchanged)
└── caddy/                      # Existing (unchanged)

docs/
├── dev/
│   └── deploy/                 # REMOVED
└── ops-pack/
    ├── loop-sites-matrix.md    # Updated
    └── what-broke-last-time.md # Potentially updated
```

---

## Verification

### After Each Task Merge

```bash
git checkout feature/initial-deploy
git pull origin feature/initial-deploy
make lint && make test
```

### Before Feature PR

```bash
git fetch origin
git rebase origin/release/0.6.0
make lint && make test

# Verify documentation links still work
grep -r "docs/dev/deploy" . --include="*.md" | grep -v "initial-deploy"
```

### Post-Deployment Verification

```bash
# From your local machine
curl -i "https://sage-and-stone.lintel.site/health/"
curl -i "https://sage-and-stone.lintel.site/"

# Verify admin is protected (should not be publicly accessible)
curl -i "https://sage-and-stone.lintel.site/admin/"
```

---

## Risk

**Level:** Medium

**Factors:**

- First real deployment — process not yet muscle memory
- SSH key management introduces security surface
- VPS provisioning has many manual steps
- DNS propagation may cause delays

**Mitigation:**

- Follow vps-golden-path.md step-by-step
- Test SSH access before attempting deploy
- Use staging domain (disposable if issues)
- Document everything in what-broke-last-time.md

---

## Labels

- [ ] `type:work-order`
- [ ] `component:infrastructure`
- [ ] `component:docs`
- [ ] `risk:medium`
- [ ] Milestone: `v0.6.0`

---

## Definition of Done

- [ ] All documentation subtasks merged to feature branch
- [ ] VPS provisioned and accessible via SSH
- [ ] Sage & Stone deployed to `sage-and-stone.lintel.site`
- [ ] `/health/` returns HTTP 200
- [ ] Homepage renders correctly
- [ ] Loop sites matrix updated
- [ ] Any issues documented in what-broke-last-time.md
- [ ] Feature branch merged to release/0.6.0 (PR approved)
- [ ] Version Declaration #190 updated
