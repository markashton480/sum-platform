# TEST-007 Follow-up

## Summary
- Audited destructive filesystem operations and replaced remaining unsafe deletions.
- CLI check test now simulates missing CSS without direct unlink in tmp output.
- CI guard now fails on any tracked or untracked changes in protected paths.
- Ticket docs updated (TEST-007 marked cancelled; TEST-007R added).

## Commands run
- `rg -n "shutil\.rmtree|\brmtree\(|rm -rf|Path\.unlink\(|\.unlink\(|rmdir\(|os\.remove\(|os\.unlink\(|Path\.rmdir\(" tests cli/tests -g"*.py"`
  Output:
  
  ```
  tests/utils/test_safe_cleanup.py:47:        shutil.rmtree(outside, ignore_errors=True)
  tests/utils/test_safe_cleanup.py:59:        shutil.rmtree(git_dir, ignore_errors=True)
  cli/tests/test_cli_init_and_check.py:188:    css_path.unlink()
  tests/utils/safe_cleanup.py:63:    shutil.rmtree(resolved_path, ignore_errors=False)
  tests/conftest.py:146:    Guarded shutil.rmtree for tests.
  ```
- `rg -n "delete\(|remove\(|unlink\(" tests cli/tests -g"*.py"`
  Output:
  
  ```
  cli/tests/test_cli_init_and_check.py:117:        sys.path.remove(str(project))
  cli/tests/test_cli_init_and_check.py:188:    css_path.unlink()
  tests/conftest.py:139:        homepage.delete()
  tests/navigation/test_templatetags.py:268:        Page.objects.exclude(pk=root.pk).filter(slug__startswith="nav-test-").delete()
  tests/navigation/test_cache.py:470:        ).delete()
  tests/navigation/test_models.py:266:        HeaderNavigation.objects.filter(site=default_site).delete()
  tests/navigation/test_models.py:267:        HeaderNavigation.objects.filter(site=second_site).delete()
  tests/navigation/test_models.py:297:        FooterNavigation.objects.filter(site=default_site).delete()
  tests/navigation/test_models.py:298:        FooterNavigation.objects.filter(site=second_site).delete()
  tests/navigation/test_models.py:326:        HeaderNavigation.objects.filter(site=default_site).delete()
  tests/navigation/test_models.py:327:        HeaderNavigation.objects.filter(site=second_site).delete()
  tests/leads/test_lead_submission_handler.py:21:    LeadSourceRule.objects.all().delete()
  tests/leads/test_attribution.py:21:    LeadSourceRule.objects.all().delete()
  tests/seo/test_seo_tags.py:24:            existing.delete()
  tests/seo/test_sitemap_robots.py:23:            existing.delete()
  tests/seo/test_sitemap_robots.py:235:        other_site.delete()
  tests/seo/test_sitemap_robots.py:247:            existing.delete()
  tests/seo/test_schema.py:30:            existing.delete()
  tests/seo/test_schema.py:238:        SiteSettings.objects.filter(site=site).delete()
  tests/forms/test_form_submission.py:646:        FormConfiguration.objects.filter(site=wagtail_site).delete()
  tests/forms/test_form_submission.py:657:        FormConfiguration.objects.filter(site=wagtail_site).delete()
  tests/forms/test_form_submission.py:671:        FormConfiguration.objects.filter(site=wagtail_site).delete()
  ```
- `source .venv/bin/activate && make lint`
  Output:
  
  ```
  ruff check . --config pyproject.toml
  All checks passed!
  mypy core cli tests
  Success: no issues found in 249 source files
  black --check core cli tests
  ```
  Result: timed out after ~200s while running Black.
- `source .venv/bin/activate && black --check core cli tests`
  Output: no output before timing out after ~200s.
- `source .venv/bin/activate && black --check core cli tests` (second attempt)
  Output: no output; aborted by user after ~400s.

## Tests not run
- `pytest -q`
- `pytest -q cli/tests tests/themes`

## Commits
- `51ce12b` test(TEST-007): audit filesystem safety + tighten CI untracked guard
- docs commit: (this commit)

## Changed files
- .github/workflows/ci.yml
- cli/tests/test_cli_init_and_check.py
- tests/utils/test_safe_cleanup.py
- docs/dev/Tasks/TEST/TEST-007.md
- docs/dev/Tasks/TEST/TEST-007R.md
- docs/dev/Tasks/TEST/TEST-007_followup.md
