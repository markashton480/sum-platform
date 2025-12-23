from __future__ import annotations

from tests.utils import REPO_ROOT

THEME_A_BLOCKS_DIR = (
    REPO_ROOT / "themes" / "theme_a" / "templates" / "sum_core" / "blocks"
)

REQUIRED_BLOCK_TEMPLATES = [
    "content_editorial_header.html",
    "content_richtext.html",
    "content_quote.html",
    "content_image.html",
    "content_buttons.html",
    "team_members.html",
]


def test_theme_a_editorial_block_overrides_exist() -> None:
    missing = [
        name
        for name in REQUIRED_BLOCK_TEMPLATES
        if not (THEME_A_BLOCKS_DIR / name).exists()
    ]
    assert not missing, f"Missing Theme A block overrides: {', '.join(missing)}"
