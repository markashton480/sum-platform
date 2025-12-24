# SQ-003 Follow-up

## Files changed
- boilerplate/project_name/settings/base.py
- cli/sum_cli/boilerplate/project_name/settings/base.py
- clients/showroom/showroom/settings/base.py
- cli/tests/test_theme_init.py
- docs/dev/SHOWROOM.md

## Commands run
- /home/mark/workspaces/sum-platform/.venv/bin/python -m pytest cli/tests/test_theme_init.py::test_init_settings_include_canonical_theme_override -q
- SUM_CANONICAL_THEME_ROOT=/home/mark/workspaces/sum-platform/themes/theme_a /home/mark/workspaces/sum-platform/.venv/bin/python /home/mark/workspaces/sum-platform/clients/showroom/manage.py shell -c "from django.template.loader import get_template; t=get_template('theme/base.html'); print(t.origin.name)"

## Verification output
```
/home/mark/workspaces/sum-platform/themes/theme_a/templates/theme/base.html
```
