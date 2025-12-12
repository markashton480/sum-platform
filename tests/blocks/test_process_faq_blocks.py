"""
Name: Process & FAQ Block Tests
Path: tests/blocks/test_process_faq_blocks.py
Purpose: Unit tests for ProcessStepsBlock and FAQBlock logic and validation.
"""

import json

import pytest
from sum_core.blocks.process_faq import FAQBlock, ProcessStepsBlock


def test_process_steps_block_structure():
    block = ProcessStepsBlock()
    assert block.child_blocks.keys() == {"eyebrow", "heading", "intro", "steps"}
    assert block.child_blocks["steps"].child_block.child_blocks.keys() == {
        "number",
        "title",
        "description",
    }


def test_process_steps_validation_error_min_items():
    block = ProcessStepsBlock()
    # Min 3 items required
    bad_value = {
        "heading": "Test",
        "steps": [
            {"title": "Step 1", "description": ""},
            {"title": "Step 2", "description": ""},
        ],
    }
    with pytest.raises(Exception):  # ValidationError from Wagtail usually
        block.clean(bad_value)


def test_faq_block_structure():
    block = FAQBlock()
    assert block.child_blocks.keys() == {
        "eyebrow",
        "heading",
        "intro",
        "items",
        "allow_multiple_open",
    }
    assert block.child_blocks["items"].child_block.child_blocks.keys() == {
        "question",
        "answer",
    }


def test_faq_schema_generation():
    block = FAQBlock()
    value = {
        "items": [
            {"question": "What is this?", "answer": "<p>This is a <b>test</b>.</p>"},
            {"question": "Who are you?", "answer": "Just a test."},
        ],
        "heading": "FAQ",
    }

    context = block.get_context(value)
    assert "faq_schema_json" in context

    schema = json.loads(context["faq_schema_json"])
    assert schema["@type"] == "FAQPage"
    assert len(schema["mainEntity"]) == 2

    assert schema["mainEntity"][0]["name"] == "What is this?"
    assert schema["mainEntity"][0]["acceptedAnswer"]["text"] == "This is a test."

    assert schema["mainEntity"][1]["name"] == "Who are you?"
