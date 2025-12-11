"""
Name: Form Blocks
Path: core/sum_core/blocks/forms.py
Purpose: StreamField blocks for contact and quote request forms
Family: SUM Platform – StreamField Blocks
Dependencies: Wagtail core blocks, PageStreamBlock, templates in sum_core/blocks
"""


from wagtail.blocks import CharBlock, RichTextBlock, StructBlock, TextBlock, BooleanBlock


class ContactFormBlock(StructBlock):
    heading = RichTextBlock(required=True, help_text="Section heading")
    intro = RichTextBlock(required=False, help_text="Optional introductory copy")
    success_message = TextBlock(required=False, default="Thanks, we’ll be in touch shortly.")
    submit_label = CharBlock(required=False, default="Send enquiry")

    class Meta:
        icon = "mail"
        template = "sum_core/blocks/contact_form.html"
        label = "Contact form"
        form_type = "contact"  # metadata for leads system


class QuoteRequestFormBlock(StructBlock):
    heading = RichTextBlock(required=True)
    intro = RichTextBlock(required=False)
    success_message = TextBlock(required=False, default="Thanks, we’ll prepare your quote.")
    submit_label = CharBlock(required=False, default="Request a quote")
    show_compact_meta = BooleanBlock(required=False, help_text="Compact layout for sidebars/short sections.")

    class Meta:
        icon = "form"
        template = "sum_core/blocks/quote_request_form.html"
        label = "Quote request form"
        form_type = "quote"
