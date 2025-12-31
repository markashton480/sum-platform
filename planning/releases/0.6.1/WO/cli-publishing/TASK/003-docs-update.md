# Task

**Title:** `WO-CLI-003: Update installation documentation`

---

## Parent

**Work Order:** WO: CLI v2 Publishing & Distribution (v0.6.1)
**Tracking Issue:** #457

---

## Branch

| Branch | Target |
|--------|--------|
| `feature/cli-publishing/003-docs-update` | `feature/cli-publishing` |

```bash
git checkout feature/cli-publishing
git pull origin feature/cli-publishing
git checkout -b feature/cli-publishing/003-docs-update
git push -u origin feature/cli-publishing/003-docs-update
```

---

## Deliverable

This task will deliver:

- Updated CLI documentation with pip installation instructions
- Updated quickstart guide
- Updated README with new installation method
- Clear migration guide for existing users

---

## Boundaries

### Do

- Update `docs/cli.md` with pip installation
- Update `docs/quickstart.md` with new installation method
- Update CLI README with installation instructions
- Add migration notes for users of previous versions
- Document both pip and git-based installation methods
- Verify all code examples work

### Do NOT

- ❌ Do not modify CLI code
- ❌ Do not change other documentation
- ❌ Do not add new features to docs
- ❌ Do not remove git-based installation (keep as alternative)

---

## Acceptance Criteria

- [ ] `docs/cli.md` includes `pip install sum-cli` instructions
- [ ] `docs/quickstart.md` updated with pip installation
- [ ] `cli/README.md` updated with installation instructions
- [ ] Migration notes for existing users included
- [ ] All code examples tested and working
- [ ] Documentation builds without errors

---

## Test Commands

```bash
make lint
make test

# Build docs (if using mkdocs or similar)
# mkdocs build

# Verify installation instructions work
python -m venv test-env
source test-env/bin/activate
# Follow the documented installation steps
```

---

## Files Expected to Change

```
docs/
├── cli.md                  # Modified: pip installation
└── quickstart.md           # Modified: updated install steps

cli/
└── README.md               # Modified: installation instructions
```

---

## Dependencies

**Depends On:**
- [ ] WO-CLI-002: Test on PyPI Test instance

**Blocks:**
- Nothing — can be done in parallel with WO-CLI-004

---

## Risk

**Level:** Low

**Why:**
- Documentation only, no code changes
- Easy to update if issues found

---

## Labels

- [ ] `type:task`
- [ ] `component:docs`
- [ ] `component:cli`
- [ ] `risk:low`
- [ ] Milestone: `v0.6.1`

---

## Definition of Done

- [ ] Acceptance criteria met
- [ ] `make lint && make test` passes
- [ ] PR merged to feature branch
- [ ] **Model Used** field set
- [ ] `model:*` label applied
- [ ] Parent Work Order updated

---

## Commit Message

```
docs(cli): update installation instructions for CLI v2.0.0

- Add pip install sum-cli instructions
- Update quickstart guide with new installation
- Add migration notes for existing users
- Keep git-based installation as alternative

Closes #TBD
```

---

## Documentation Template

### Installation Section Update

```markdown
## Installation

### Via pip (Recommended)

```bash
pip install sum-cli
```

### Via pipx (Isolated)

```bash
pipx install sum-cli
```

### From Source

```bash
git clone https://github.com/markashton480/sum-platform.git
cd sum-platform/cli
pip install -e .
```

### Verify Installation

```bash
sum --version  # Should show 2.0.0
sum --help     # Show available commands
```
```
