from __future__ import annotations

import re
from pathlib import Path

THEME_A_DIR = Path(__file__).resolve().parent.parent.parent / "themes" / "theme_a"


def test_theme_a_tailwind_config_references_branding() -> None:
    """
    Assert that Theme A tailwind.config.js references branding variables.
    """
    config_path = THEME_A_DIR / "tailwind" / "tailwind.config.js"
    assert config_path.exists(), "Theme A tailwind config not found"

    content = config_path.read_text()

    # Check for primary/brand HSL usage
    assert "var(--brand-h" in content
    assert "var(--brand-s" in content
    assert "var(--brand-l" in content

    # Check for secondary HSL usage
    assert "var(--secondary-h" in content

    # Check for accent HSL usage
    assert "var(--accent-h" in content

    # Check for font usage
    assert "var(--font-heading" in content
    assert "var(--font-body" in content

    # Check for semantic neutral usage
    assert "var(--text-h" in content
    assert "var(--background-h" in content
    assert "var(--surface-h" in content


def test_theme_a_input_css_no_hardcoded_hex() -> None:
    """
    Assert that Theme A input.css does not contain prohibited hardcoded hex values
    in places where dynamic branding should be used.
    """
    css_path = THEME_A_DIR / "static" / "theme_a" / "css" / "input.css"
    assert css_path.exists(), "Theme A input.css not found"

    content = css_path.read_text()

    # Prohibited hex values (case insensitive check)
    prohibited_hexes = [
        "#F7F5F1",  # Linen (Background)
        "#1A2F23",  # Black (Text)
        "#E3DED4",  # Oat (Surface)
        "#A0563B",  # Terra (Primary/Accent)
        "#8F8D88",  # Stone (Neutral)
    ]

    # Removing the :root block definition from the check is tricky without parsing.
    # However, I left them in :root.
    # The requirement is "No literal #xxxxxx in its base layer for brand-driven surfaces/text/focus".

    # We can perform a simpler check: verify that '@layer base' block DOES NOT contain these hexes.

    # Extract @layer base content
    layer_base_match = re.search(r"@layer base \{(.*?)\}", content, re.DOTALL)
    assert layer_base_match, "@layer base block not found"

    layer_base_content = layer_base_match.group(1).upper()

    for hex_code in prohibited_hexes:
        assert (
            hex_code not in layer_base_content
        ), f"Found prohibited hex {hex_code} in @layer base"

    # Also check Accessibility section (focus outlines)
    # This is usually in @layer components or just root level styles
    # In input.css, it was around line 570.

    # Let's search for the Accessibility section
    # "SECTION 12: ACCESSIBILITY"
    access_match = re.search(
        r"SECTION 12: ACCESSIBILITY(.*?)(SECTION 13|$)", content, re.DOTALL
    )
    if access_match:
        access_content = access_match.group(1).upper()
        # Terra #A0563B
        assert (
            "#A0563B" not in access_content
        ), "Found prohibited hex #A0563B in Accessibility section"
