"""
Backwards compatibility tests for blog and dynamic forms.

Ensures that:
1. Static forms and dynamic forms coexist peacefully
2. Existing Lead model works with both form types
3. No breaking changes to existing functionality
4. Migration path is safe
"""

import pytest
from django.contrib.auth import get_user_model
from sum_core.forms.models import FormDefinition
from sum_core.leads.models import Lead
from sum_core.pages.blog import BlogIndexPage, BlogPostPage, Category
from sum_core.pages.models import StandardPage
from wagtail.models import Site

User = get_user_model()


@pytest.mark.django_db
class TestStaticFormCompatibility:
    """Test that static forms continue to work alongside dynamic forms."""

    @pytest.fixture
    def site(self):
        """Get the default test site."""
        return Site.objects.get(is_default_site=True)

    def test_static_contact_form_still_works(self, client, site):
        """Test that the original static contact form still functions."""
        home = site.root_page

        # Create page with static contact form block
        page = StandardPage(
            title="Static Contact",
            slug="static-contact",
            body=[
                ("rich_text", "<h2>Contact Us (Static Form)</h2>"),
                (
                    "contact_form",
                    {
                        "heading": "<p>Get in Touch</p>",
                        "intro": "<p>Fill out the form below.</p>",
                        "submit_label": "Send",
                    },
                ),
            ],
        )
        home.add_child(instance=page)
        page.save_revision().publish()

        # Load the page
        response = client.get(page.get_url())
        assert response.status_code == 200
        content = response.content.decode()

        # Static form should be present
        assert "Get in Touch" in content

    def test_static_quote_request_form_still_works(self, client, site):
        """Test that the static quote request form still functions."""
        home = site.root_page

        # Create page with static quote request form block
        page = StandardPage(
            title="Quote Request",
            slug="quote-request-static",
            body=[
                ("rich_text", "<h2>Request a Quote (Static Form)</h2>"),
                (
                    "quote_request_form",
                    {
                        "heading": "<p>Get Your Free Quote</p>",
                        "intro": "<p>We'll respond within 24 hours.</p>",
                        "submit_label": "Request Quote",
                    },
                ),
            ],
        )
        home.add_child(instance=page)
        page.save_revision().publish()

        # Load the page
        response = client.get(page.get_url())
        assert response.status_code == 200
        content = response.content.decode()

        # Static form should be present
        assert "Get Your Free Quote" in content

    def test_static_and_dynamic_forms_coexist_on_same_page(self, client, site):
        """Test that static and dynamic forms can exist on the same page."""
        home = site.root_page

        # Create a dynamic form
        dynamic_form = FormDefinition.objects.create(
            name="Newsletter",
            slug="newsletter-compat",
            site=site,
            fields=[
                (
                    "email_input",
                    {"field_name": "email", "label": "Email", "required": True},
                ),
                (
                    "textarea",
                    {"field_name": "message", "label": "Message", "required": True},
                ),
            ],
            success_message="Subscribed!",
            is_active=True,
        )

        # Create page with both static and dynamic forms
        page = StandardPage(
            title="Mixed Forms",
            slug="mixed-forms",
            body=[
                ("rich_text", "<h2>Static Contact Form</h2>"),
                (
                    "contact_form",
                    {
                        "heading": "<p>Contact Us</p>",
                        "intro": "<p>Static form</p>",
                        "submit_label": "Send",
                    },
                ),
                ("rich_text", "<h2>Dynamic Newsletter Form</h2>"),
                (
                    "dynamic_form",
                    {
                        "form_definition": dynamic_form,
                        "presentation_style": "inline",
                        "cta_button_text": "Subscribe",
                    },
                ),
            ],
        )
        home.add_child(instance=page)
        page.save_revision().publish()

        # Load the page
        response = client.get(page.get_url())
        assert response.status_code == 200
        content = response.content.decode()

        # Both forms should be present
        assert "Static Contact Form" in content
        assert "Dynamic Newsletter Form" in content
        assert "Contact Us" in content
        assert "Subscribe" in content


@pytest.mark.django_db
class TestLeadModelBackwardsCompatibility:
    """Test that Lead model works with both static and dynamic forms.

    form_data Structure Documentation:
    ---------------------------------
    Static Forms (contact, quote, etc.):
        - form_type: identifies the static form type (e.g., "contact", "quote")
        - form_data: empty dict {} or may contain raw form field data
        - No form_definition_slug since static forms aren't in FormDefinition table

    Dynamic Forms:
        - form_type: matches the FormDefinition slug for the submitted form
        - form_data: contains non-core fields + ip_address (no slug stored today)

    This distinction exists because:
    1. Static forms are hardcoded in templates (contact_form, quote_request_form blocks)
    2. Dynamic forms are defined in FormDefinition model and rendered via DynamicFormBlock
    3. Backwards compatibility requires supporting both patterns
    """

    @pytest.fixture
    def site(self):
        """Get the default test site."""
        return Site.objects.get(is_default_site=True)

    def test_lead_from_static_forms_works(self):
        """Test that Leads can be created from static forms (legacy behavior).

        Static forms use form_type to identify the form and may have empty form_data.
        """
        # Create lead from static form (using form_type to identify form)
        lead = Lead.objects.create(
            name="Legacy User",
            email="legacy@example.com",
            phone="555-0000",
            message="Legacy message",
            form_type="contact",  # Static form type
        )

        assert lead.id is not None
        assert lead.form_type == "contact"
        # Static forms don't have form_definition_slug - form_data may be empty
        assert "form_definition_slug" not in lead.form_data

    def test_lead_from_dynamic_forms_works(self, site):
        """Test that Leads can store dynamic form metadata in form_data."""
        lead = Lead.objects.create(
            name="Modern User",
            email="modern@example.com",
            message="Dynamic form submission",
            form_type="dynamic-compat",
            form_data={"company": "Acme"},
        )

        assert lead.id is not None
        assert lead.form_type == "dynamic-compat"
        assert lead.form_data["company"] == "Acme"

    def test_lead_admin_works_with_both_types(self, site):
        """Test that Lead admin can display both static and dynamic form leads."""
        # Create static form lead
        static_lead = Lead.objects.create(
            name="Static Lead",
            email="static@example.com",
            message="Static form message",
            form_type="contact",
        )

        # Create dynamic form lead
        dynamic_lead = Lead.objects.create(
            name="Dynamic Lead",
            email="dynamic@example.com",
            message="Dynamic form message",
            form_type="dynamic-admin",
            form_data={"company": "Admin Co"},
        )

        # Both should be queryable
        all_leads = Lead.objects.all()
        assert static_lead in all_leads
        assert dynamic_lead in all_leads

    def test_lead_attribution_fields_work_for_both_types(self):
        """Test that attribution fields work regardless of form type."""
        # Static form lead with attribution
        static_lead = Lead.objects.create(
            name="Static Attribution",
            email="static-attr@example.com",
            message="Testing attribution fields",
            form_type="quote",
            utm_source="google",
            utm_campaign="test",
            referrer_url="https://google.com",
        )

        assert static_lead.utm_source == "google"
        assert static_lead.utm_campaign == "test"
        assert static_lead.referrer_url == "https://google.com"


@pytest.mark.django_db
class TestFormSubmissionBackwardsCompatibility:
    """Test that form submissions work for both static and dynamic forms."""

    @pytest.fixture
    def site(self):
        """Get the default test site."""
        return Site.objects.get(is_default_site=True)

    def test_static_form_submission_creates_lead(self, client, site):
        """Test that static form submissions still create Leads."""
        home = site.root_page
        page = StandardPage(
            title="Static Form Page",
            slug="static-form-page",
            body=[
                (
                    "contact_form",
                    {
                        "heading": "<p>Contact</p>",
                        "intro": "<p>Get in touch</p>",
                        "submit_label": "Send",
                    },
                ),
            ],
        )
        home.add_child(instance=page)
        page.save_revision().publish()

        client.get(page.get_url())

        # Submit static contact form
        form_data = {
            "form_type": "contact",  # Static form type
            "name": "Static Submitter",
            "email": "static@example.com",
            "phone": "555-1111",
            "message": "Static form message",
            "page_url": page.get_url(),
            "landing_page_url": page.get_url(),
            "csrfmiddlewaretoken": client.cookies.get("csrftoken").value,
        }

        response = client.post("/forms/submit/", data=form_data)
        assert response.status_code == 200

        # Lead should be created
        lead = Lead.objects.get(email="static@example.com")
        assert lead.name == "Static Submitter"
        assert lead.form_type == "contact"
        # Static forms don't have form_definition_slug in form_data
        assert "form_definition_slug" not in lead.form_data

    def test_dynamic_form_submission_creates_lead(self, client, site):
        """Test that dynamic form submissions create Leads."""
        home = site.root_page

        form = FormDefinition.objects.create(
            name="Compat Dynamic Form",
            slug="compat-dynamic",
            site=site,
            fields=[
                (
                    "text_input",
                    {"field_name": "name", "label": "Name", "required": True},
                ),
                (
                    "email_input",
                    {"field_name": "email", "label": "Email", "required": True},
                ),
                (
                    "textarea",
                    {"field_name": "message", "label": "Message", "required": True},
                ),
            ],
            success_message="Success!",
            is_active=True,
        )

        page = StandardPage(
            title="Dynamic Form Page",
            slug="dynamic-form-page",
            body=[
                (
                    "dynamic_form",
                    {
                        "form_definition": form,
                        "presentation_style": "inline",
                    },
                ),
            ],
        )
        home.add_child(instance=page)
        page.save_revision().publish()

        client.get(page.get_url())

        # Submit dynamic form
        form_data = {
            "form_definition_id": form.id,
            "name": "Dynamic Submitter",
            "email": "dynamic@example.com",
            "message": "Dynamic form message",
            "page_url": page.get_url(),
            "landing_page_url": page.get_url(),
            "csrfmiddlewaretoken": client.cookies.get("csrftoken").value,
        }

        response = client.post("/forms/submit/", data=form_data)
        assert response.status_code == 200

        # Lead should be created
        lead = Lead.objects.get(email="dynamic@example.com")
        assert lead.name == "Dynamic Submitter"
        assert lead.form_type == form.slug
        assert "ip_address" in lead.form_data


@pytest.mark.django_db
class TestBlogBackwardsCompatibility:
    """Test that blog functionality is backwards compatible."""

    @pytest.fixture
    def site(self):
        """Get the default test site."""
        return Site.objects.get(is_default_site=True)

    def test_blog_works_without_dynamic_forms(self, client, site):
        """Test that blog pages work without any embedded forms."""
        home = site.root_page

        blog_index = BlogIndexPage(title="Blog", slug="blog-compat", posts_per_page=10)
        home.add_child(instance=blog_index)
        blog_index.save_revision().publish()

        category = Category.objects.create(name="Compat Test", slug="compat-test")

        # Create post without any forms
        post = BlogPostPage(
            title="Post Without Forms",
            slug="post-without-forms",
            body=[
                (
                    "rich_text",
                    "<h2>Article Heading</h2><p>" + "Article content. " * 50 + "</p>",
                ),
            ],
            category=category,
        )
        blog_index.add_child(instance=post)
        post.save_revision().publish()

        # Should render correctly
        response = client.get(post.get_url())
        assert response.status_code == 200
        content = response.content.decode()
        assert "Post Without Forms" in content
        assert "Article Heading" in content

    def test_existing_blog_fields_still_work(self, site):
        """Test that all original blog fields continue to function."""

        home = site.root_page

        blog_index = BlogIndexPage(title="Blog", slug="blog-fields", posts_per_page=10)
        home.add_child(instance=blog_index)
        blog_index.save_revision().publish()

        category = Category.objects.create(name="Field Test", slug="field-test")

        # Create post with all traditional fields
        post = BlogPostPage(
            title="Traditional Post",
            slug="traditional-post",
            excerpt="Manual excerpt",
            body=[("rich_text", "<p>" + "Body content. " * 100 + "</p>")],
            category=category,
            author_name="Test Author",
            # published_date defaults to timezone.now() per model definition
        )
        blog_index.add_child(instance=post)
        post.save_revision().publish()

        # Verify all fields work
        assert post.title == "Traditional Post"
        assert post.excerpt == "Manual excerpt"
        assert post.category == category
        assert post.author_name == "Test Author"
        assert post.published_date is not None  # Auto-set by default
        assert post.reading_time > 0  # Auto-calculated


@pytest.mark.django_db
class TestMigrationSafety:
    """Test that migrations from pre-dynamic-forms state are safe."""

    def test_lead_model_form_data_supports_dynamic_forms(self):
        """Test that form_data JSONField supports dynamic form metadata."""
        lead = Lead.objects.create(
            name="Form Data Test",
            email="formdata@example.com",
            message="Testing form_data field",
            form_type="dynamic",
            form_data={"company": "Test Co"},
        )

        # Verify form_data stores extra fields
        assert hasattr(lead, "form_data")
        assert lead.form_data.get("company") == "Test Co"

        # Verify form_data can be empty for static forms (backwards compat)
        static_lead = Lead.objects.create(
            name="Static Form Test",
            email="static@example.com",
            message="Testing static form",
            form_type="contact",
            form_data={},  # Empty for static forms
        )
        assert static_lead.form_data == {}

    def test_form_type_field_still_exists(self):
        """Test that form_type field still exists for static forms."""
        # Create a lead and verify form_type field works
        lead = Lead.objects.create(
            name="Type Test",
            email="type@example.com",
            message="Testing form_type field",
            form_type="contact",  # Should still work
        )

        assert hasattr(lead, "form_type")
        assert lead.form_type == "contact"

    def test_existing_leads_continue_to_work(self):
        """Test that existing Leads continue to work with standard fields."""
        # Simulate an old lead (using core Lead model fields)
        old_lead = Lead.objects.create(
            name="Old Lead",
            email="old@example.com",
            phone="555-0000",
            message="Before dynamic forms",
            form_type="quote",
            # Optional fields like form_data can be empty
        )

        # Should be able to retrieve and work with it
        retrieved = Lead.objects.get(id=old_lead.id)
        assert retrieved.name == "Old Lead"
        assert retrieved.form_type == "quote"
        assert retrieved.message == "Before dynamic forms"


@pytest.mark.django_db
class TestPageTypeCompatibility:
    """Test that page types are backwards compatible."""

    @pytest.fixture
    def site(self):
        """Get the default test site."""
        return Site.objects.get(is_default_site=True)

    def test_standard_page_works_with_all_block_types(self, site):
        """Test that StandardPage supports both old and new blocks."""
        home = site.root_page

        # Create FormDefinition for dynamic form
        form = FormDefinition.objects.create(
            name="Page Compat Form",
            slug="page-compat",
            site=site,
            fields=[
                (
                    "email_input",
                    {"field_name": "email", "label": "Email", "required": True},
                ),
                (
                    "textarea",
                    {"field_name": "message", "label": "Message", "required": True},
                ),
            ],
            is_active=True,
        )

        # StandardPage should support all block types
        page = StandardPage(
            title="All Blocks",
            slug="all-blocks",
            body=[
                ("rich_text", "<h2>Heading Block</h2><p>Paragraph block</p>"),
                (
                    "contact_form",
                    {"heading": "<p>Static Contact</p>", "intro": "<p>Old</p>"},
                ),
                (
                    "quote_request_form",
                    {"heading": "<p>Static Quote</p>", "intro": "<p>Old</p>"},
                ),
                (
                    "dynamic_form",
                    {
                        "form_definition": form,
                        "presentation_style": "inline",
                    },
                ),  # New
            ],
        )
        home.add_child(instance=page)
        page.save_revision().publish()

        # All blocks should be present
        assert len(page.body) == 4
        assert page.body[0].block_type == "rich_text"
        assert page.body[1].block_type == "contact_form"
        assert page.body[2].block_type == "quote_request_form"
        assert page.body[3].block_type == "dynamic_form"

    def test_blog_post_page_backwards_compatible_with_static_blocks(self, site):
        """Test that BlogPostPage can use traditional blocks."""
        home = site.root_page

        blog_index = BlogIndexPage(title="Blog", slug="blog-static", posts_per_page=10)
        home.add_child(instance=blog_index)
        blog_index.save_revision().publish()

        category = Category.objects.create(name="Static Blocks", slug="static-blocks")

        # BlogPostPage with content blocks (no forms)
        post = BlogPostPage(
            title="Traditional Blocks Post",
            slug="traditional-blocks",
            body=[
                ("rich_text", "<h2>Introduction</h2><p>Paragraph content.</p>"),
                ("rich_text", "<h2>Conclusion</h2>"),
            ],
            category=category,
        )
        blog_index.add_child(instance=post)
        post.save_revision().publish()

        # Should work fine
        assert len(post.body) >= 2  # At minimum two rich_text blocks
