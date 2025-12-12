import pytest
from sum_core.blocks.base import PageStreamBlock
from sum_core.blocks.forms import ContactFormBlock, QuoteRequestFormBlock


@pytest.mark.django_db
class TestFormBlocks:
    def test_contact_form_block_definitions(self):
        block = ContactFormBlock()
        fields = block.child_blocks
        assert "eyebrow" in fields
        assert "heading" in fields
        assert "intro" in fields
        assert "success_message" in fields
        assert "submit_label" in fields
        assert block.meta.form_type == "contact"
        assert block.meta.template == "sum_core/blocks/contact_form.html"

    def test_quote_request_form_block_definitions(self):
        block = QuoteRequestFormBlock()
        fields = block.child_blocks
        assert "eyebrow" in fields
        assert "heading" in fields
        assert "intro" in fields
        assert "success_message" in fields
        assert "submit_label" in fields
        assert "show_compact_meta" in fields
        assert block.meta.form_type == "quote"
        assert block.meta.template == "sum_core/blocks/quote_request_form.html"

    def test_pagestreamblock_registration(self):
        stream_block = PageStreamBlock()
        # Debug available blocks
        print(f"DEBUG: child_blocks keys: {stream_block.child_blocks.keys()}")

        assert (
            "contact_form" in stream_block.child_blocks
        ), f"contact_form not found in {stream_block.child_blocks.keys()}"
        assert "quote_request_form" in stream_block.child_blocks

        contact = stream_block.child_blocks["contact_form"]
        assert isinstance(contact, ContactFormBlock)

        quote = stream_block.child_blocks["quote_request_form"]
        assert isinstance(quote, QuoteRequestFormBlock)
