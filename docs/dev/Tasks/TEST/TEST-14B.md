# TEST-014B — Final close-out for PR #16

## Objective
Finish cleaning PR #16 by:
1. Removing any remaining hidden/bidi Unicode characters flagged by GitHub.  
2. Ensuring `theme_dir` fixture uses dynamic discovery (not hard-coded).  
3. Committing this ticket **and** its follow-up on the same branch (`test/TEST-014-theme-conftest`).  

---

## Steps

### 1. Prep
```bash
git fetch origin
git checkout test/TEST-014-theme-conftest
git pull --ff-only origin test/TEST-014-theme-conftest
````


### 2. Remove any hidden Unicode characters

```bash
python - <<'PY'
import pathlib, unicodedata
files = pathlib.Path("tests/themes").rglob("*.py")
SUSP = {"Cf","Zs"}
for f in files:
    text = f.read_text("utf-8")
    bad = [c for c in text if unicodedata.category(c) in SUSP]
    if bad:
        print("Unicode controls found in", f)
        raise SystemExit(1)
print("No hidden Unicode chars found.")
PY
```

If any found, re-type those lines and re-run until clean.
Then:

```bash
git add tests/themes
git commit -m "fix(TEST-014B): remove hidden unicode characters"
git push
```

### 4. Fix theme discovery

In `tests/themes/conftest.py`, make sure:

```python
THEMES_ROOT = REPO_ROOT / "themes"

@pytest.fixture(scope="session", params=[p.name for p in THEMES_ROOT.iterdir() if p.is_dir()])
def theme_dir(request):
    """Yield each available theme directory."""
    return THEMES_ROOT / request.param
```

Commit:

```bash
git add tests/themes/conftest.py
git commit -m "refactor(TEST-014B): make theme_dir fixture discover themes dynamically"
git push
```

### 5. Verify and record

```bash
make lint
make test-themes
make test-templates
make test
git status --porcelain
```

Paste results into `docs/dev/Tasks/TEST/TEST-014B_followup.md`, then:

```bash
git add docs/dev/Tasks/TEST/TEST-014B_followup.md
git commit -m "docs(TEST-014B): verification and close-out"
git push
```

---

## Expected result

* GitHub stops flagging Unicode warnings.
* Theme discovery works dynamically.
* All tests and lint pass.
* Branch clean (`git status` empty).
* PR #16 ready to merge.

```

