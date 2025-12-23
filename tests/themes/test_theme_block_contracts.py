from __future__ import annotations

from tests.utils import REPO_ROOT

THEME_A_REQUIRED_BLOCK_TEMPLATES = [
    "sum_core/blocks/process_steps.html",
    "sum_core/blocks/timeline.html",
    "sum_core/blocks/service_detail.html",
]


def test_theme_a_required_block_templates_exist() -> None:
    theme_template_root = REPO_ROOT / "themes" / "theme_a" / "templates"
    missing = [
        template
        for template in THEME_A_REQUIRED_BLOCK_TEMPLATES
        if not (theme_template_root / template).exists()
    ]
    assert not missing, f"Missing Theme A block templates: {', '.join(missing)}"
