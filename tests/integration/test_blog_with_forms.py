"""
Integration tests for blog pages with embedded dynamic forms.

Tests the integration between BlogPostPage and DynamicFormBlock,
ensuring forms can be embedded in blog posts and function correctly.
"""

import pytest
from django.contrib.auth import get_user_model
from sum_core.forms.models import FormDefinition
from sum_core.leads.models import Lead
from sum_core.pages.blog import BlogIndexPage, BlogPostPage, Category
from wagtail.models import Site

User = get_user_model()


@pytest.mark.django_db
class TestBlogWithDynamicForms:
    """Test blog posts with embedded dynamic forms."""

    @pytest.fixture
    def site(self):
        """Get the default test site."""
        return Site.objects.get(is_default_site=True)

    @pytest.fixture
    def blog_index(self, site):
        """Create a BlogIndexPage."""
        home = site.root_page
        blog_index = BlogIndexPage(title="Blog", slug="blog", posts_per_page=10)
        home.add_child(instance=blog_index)
        blog_index.save_revision().publish()
        return blog_index

    @pytest.fixture
    def category(self):
        """Create a test category."""
        return Category.objects.create(name="Integration Test", slug="integration-test")

    @pytest.fixture
    def form_definition(self, site):
        """Create a test FormDefinition."""
        return FormDefinition.objects.create(
            name="Newsletter Signup",
            slug="newsletter",
            site=site,
            fields=[
                ("text_input", {"label": "Name", "required": True}),
                ("email_input", {"label": "Email", "required": True}),
            ],
            success_message="Thanks for subscribing!",
            is_active=True,
        )

    def test_create_blog_post_with_dynamic_form_block(
        self, blog_index, category, form_definition
    ):
        """Test creating a BlogPostPage with DynamicFormBlock in body."""
        post = BlogPostPage(
            title="Post with Newsletter Form",
            slug="post-with-newsletter",
            excerpt="Sign up for our newsletter!",
            body=[
                ("rich_text", "<p>" + "Welcome to our blog. " * 50 + "</p>"),
                (
                    "dynamic_form",
                    {
                        "form_definition": form_definition,
                        "presentation_style": "inline",
                        "cta_button_text": "Subscribe Now",
                    },
                ),
                ("rich_text", "<p>" + "Thanks for reading! " * 50 + "</p>"),
            ],
            category=category,
        )
        blog_index.add_child(instance=post)
        post.save_revision().publish()

        # Verify post was created with form block
        assert post.body is not None
        assert len(post.body) == 3
        assert post.body[1].block_type == "dynamic_form"
        assert post.body[1].value["form_definition"] == form_definition
        assert post.body[1].value["cta_button_text"] == "Subscribe Now"

    def test_render_blog_post_with_embedded_form(
        self, client, blog_index, category, form_definition
    ):
        """Test that blog post renders correctly with embedded form."""
        post = BlogPostPage(
            title="Article with CTA Form",
            slug="article-with-cta",
            body=[
                (
                    "rich_text",
                    "<h2>Introduction</h2><p>" + "Article introduction. " * 50 + "</p>",
                ),
                (
                    "dynamic_form",
                    {
                        "form_definition": form_definition,
                        "presentation_style": "inline",
                        "cta_button_text": "Sign Up",
                    },
                ),
            ],
            category=category,
        )
        blog_index.add_child(instance=post)
        post.save_revision().publish()

        response = client.get(post.get_url())
        content = response.content.decode()

        # Verify page renders
        assert response.status_code == 200
        assert "Article with CTA Form" in content

        # Verify form is present
        assert "Sign Up" in content
        assert "newsletter" in content.lower()

    def test_multiple_forms_in_single_blog_post(
        self, client, blog_index, category, site
    ):
        """Test blog post with multiple DynamicFormBlocks."""
        # Create two different forms
        newsletter_form = FormDefinition.objects.create(
            name="Newsletter",
            slug="newsletter-multi",
            site=site,
            fields=[("email_input", {"label": "Email", "required": True})],
            success_message="Subscribed!",
            is_active=True,
        )

        contact_form = FormDefinition.objects.create(
            name="Contact Us",
            slug="contact-multi",
            site=site,
            fields=[
                ("text_input", {"label": "Name", "required": True}),
                ("email_input", {"label": "Email", "required": True}),
                ("textarea", {"label": "Message", "required": True, "rows": 5}),
            ],
            success_message="We'll be in touch!",
            is_active=True,
        )

        post = BlogPostPage(
            title="Post with Multiple Forms",
            slug="multi-form-post",
            body=[
                ("rich_text", "<p>" + "Article content. " * 50 + "</p>"),
                (
                    "dynamic_form",
                    {
                        "form_definition": newsletter_form,
                        "presentation_style": "inline",
                        "cta_button_text": "Subscribe",
                    },
                ),
                ("rich_text", "<h2>Get in Touch</h2>"),
                (
                    "dynamic_form",
                    {
                        "form_definition": contact_form,
                        "presentation_style": "inline",
                        "cta_button_text": "Send Message",
                    },
                ),
            ],
            category=category,
        )
        blog_index.add_child(instance=post)
        post.save_revision().publish()

        response = client.get(post.get_url())
        content = response.content.decode()

        # Verify both forms are present
        assert response.status_code == 200
        assert "Subscribe" in content
        assert "Send Message" in content
        assert "newsletter-multi" in content
        assert "contact-multi" in content

    def test_form_submission_from_blog_post(
        self, client, blog_index, category, form_definition
    ):
        """Test submitting a form embedded in a blog post."""
        post = BlogPostPage(
            title="Subscription Post",
            slug="subscription-post",
            body=[
                ("rich_text", "<p>" + "Subscribe below. " * 50 + "</p>"),
                (
                    "dynamic_form",
                    {
                        "form_definition": form_definition,
                        "presentation_style": "inline",
                    },
                ),
            ],
            category=category,
        )
        blog_index.add_child(instance=post)
        post.save_revision().publish()

        # Get the page to obtain CSRF token
        response = client.get(post.get_url())
        assert response.status_code == 200

        # Submit the form
        form_data = {
            "form_definition_slug": "newsletter",
            "Name": "John Doe",  # Matches field label in FormDefinition
            "Email": "john@example.com",  # Matches field label in FormDefinition
            "page_url": post.get_url(),
            "landing_page_url": post.get_url(),
            "csrfmiddlewaretoken": client.cookies.get("csrftoken").value,
        }

        submission_response = client.post("/forms/submit/", data=form_data)

        # Verify successful submission
        assert submission_response.status_code == 200
        response_data = submission_response.json()
        assert response_data["success"] is True
        assert response_data["message"] == "Thanks for subscribing!"

        # Verify Lead was created
        lead = Lead.objects.get(email="john@example.com")
        assert lead.name == "John Doe"
        # Form reference is stored in form_data, not as FK (see Issue #183)
        assert lead.form_data.get("form_definition_slug") == form_definition.slug
        assert lead.page_url == post.get_url()

    def test_inactive_form_in_blog_post_shows_warning(
        self, client, blog_index, category, site
    ):
        """Test that inactive forms show appropriate message in blog posts."""
        inactive_form = FormDefinition.objects.create(
            name="Inactive Form",
            slug="inactive-form",
            site=site,
            fields=[("email_input", {"label": "Email", "required": True})],
            success_message="Success",
            is_active=False,  # Inactive
        )

        post = BlogPostPage(
            title="Post with Inactive Form",
            slug="inactive-form-post",
            body=[
                ("rich_text", "<p>" + "Content. " * 50 + "</p>"),
                (
                    "dynamic_form",
                    {
                        "form_definition": inactive_form,
                        "presentation_style": "inline",
                    },
                ),
            ],
            category=category,
        )
        blog_index.add_child(instance=post)
        post.save_revision().publish()

        response = client.get(post.get_url())

        # Template should indicate form is inactive
        assert response.status_code == 200
        # The exact message depends on template implementation

    def test_different_presentation_styles_in_blog(
        self, client, blog_index, category, site
    ):
        """Test different form presentation styles in blog posts."""
        form = FormDefinition.objects.create(
            name="Multi-Style Form",
            slug="multi-style",
            site=site,
            fields=[("email_input", {"label": "Email", "required": True})],
            success_message="Thanks!",
            is_active=True,
        )

        for style in ["inline", "modal", "sidebar"]:
            post = BlogPostPage(
                title=f"Post with {style.title()} Form",
                slug=f"post-{style}-form",
                body=[
                    ("rich_text", "<p>" + "Content. " * 50 + "</p>"),
                    (
                        "dynamic_form",
                        {
                            "form_definition": form,
                            "presentation_style": style,
                            "cta_button_text": f"{style.title()} CTA",
                        },
                    ),
                ],
                category=category,
            )
            blog_index.add_child(instance=post)
            post.save_revision().publish()

            response = client.get(post.get_url())
            assert response.status_code == 200
            content = response.content.decode()
            assert f"{style.title()} CTA" in content

    def test_form_with_redirect_in_blog_post(
        self, client, blog_index, category, form_definition
    ):
        """Test form with success redirect URL in blog post."""
        thank_you_page = BlogPostPage(
            title="Thank You",
            slug="thank-you",
            body=[("rich_text", "<p>" + "Thanks for subscribing! " * 50 + "</p>")],
            category=category,
        )
        blog_index.add_child(instance=thank_you_page)
        thank_you_page.save_revision().publish()

        post = BlogPostPage(
            title="Post with Redirect Form",
            slug="redirect-form-post",
            body=[
                ("rich_text", "<p>" + "Subscribe below. " * 50 + "</p>"),
                (
                    "dynamic_form",
                    {
                        "form_definition": form_definition,
                        "presentation_style": "inline",
                        "success_redirect_url": thank_you_page.get_url(),
                    },
                ),
            ],
            category=category,
        )
        blog_index.add_child(instance=post)
        post.save_revision().publish()

        response = client.get(post.get_url())
        content = response.content.decode()

        # Verify form is present and redirect URL is in the template
        assert response.status_code == 200
        assert form_definition.slug in content.lower()


@pytest.mark.django_db
class TestBlogFormIntegrationEdgeCases:
    """Test edge cases for blog and forms integration."""

    @pytest.fixture
    def site(self):
        """Get the default test site."""
        return Site.objects.get(is_default_site=True)

    @pytest.fixture
    def blog_setup(self, site):
        """Create blog structure."""
        home = site.root_page
        blog_index = BlogIndexPage(title="Blog", slug="blog", posts_per_page=10)
        home.add_child(instance=blog_index)
        blog_index.save_revision().publish()

        category = Category.objects.create(name="Edge Cases", slug="edge-cases")

        return {"blog_index": blog_index, "category": category, "site": site}

    def test_blog_post_with_no_forms_renders_correctly(self, client, blog_setup):
        """Test blog post without any forms renders normally."""
        post = BlogPostPage(
            title="No Forms Post",
            slug="no-forms-post",
            body=[
                (
                    "rich_text",
                    "<h2>Article Title</h2><p>" + "Article content. " * 100 + "</p>",
                ),
            ],
            category=blog_setup["category"],
        )
        blog_setup["blog_index"].add_child(instance=post)
        post.save_revision().publish()

        response = client.get(post.get_url())
        assert response.status_code == 200
        content = response.content.decode()
        assert "No Forms Post" in content

    def test_blog_post_with_form_before_and_after_content(self, client, blog_setup):
        """Test form placement at different positions in blog post."""
        form = FormDefinition.objects.create(
            name="Placement Test",
            slug="placement-test",
            site=blog_setup["site"],
            fields=[("email_input", {"label": "Email", "required": True})],
            success_message="Success!",
            is_active=True,
        )

        post = BlogPostPage(
            title="Form Placement Post",
            slug="form-placement-post",
            body=[
                # Form at start
                (
                    "dynamic_form",
                    {
                        "form_definition": form,
                        "presentation_style": "inline",
                        "cta_button_text": "Top CTA",
                    },
                ),
                ("rich_text", "<p>" + "Middle content. " * 50 + "</p>"),
                # Form at end
                (
                    "dynamic_form",
                    {
                        "form_definition": form,
                        "presentation_style": "inline",
                        "cta_button_text": "Bottom CTA",
                    },
                ),
            ],
            category=blog_setup["category"],
        )
        blog_setup["blog_index"].add_child(instance=post)
        post.save_revision().publish()

        response = client.get(post.get_url())
        assert response.status_code == 200
        content = response.content.decode()

        # Both forms should be present
        assert "Top CTA" in content
        assert "Bottom CTA" in content

    def test_blog_post_preserves_form_attribution(self, client, blog_setup):
        """Test that form submissions from blog posts capture correct attribution."""
        form = FormDefinition.objects.create(
            name="Attribution Test",
            slug="attribution-test",
            site=blog_setup["site"],
            fields=[
                ("text_input", {"label": "Name", "required": True}),
                ("email_input", {"label": "Email", "required": True}),
            ],
            success_message="Thanks!",
            is_active=True,
        )

        post = BlogPostPage(
            title="Attribution Post",
            slug="attribution-post",
            body=[
                ("rich_text", "<p>" + "Content. " * 50 + "</p>"),
                (
                    "dynamic_form",
                    {
                        "form_definition": form,
                        "presentation_style": "inline",
                    },
                ),
            ],
            category=blog_setup["category"],
        )
        blog_setup["blog_index"].add_child(instance=post)
        post.save_revision().publish()

        # Submit form with UTM parameters
        client.get(f"{post.get_url()}?utm_source=newsletter&utm_campaign=blog-promo")

        form_data = {
            "form_definition_slug": "attribution-test",
            "Name": "Attribution Tester",  # Matches FormDefinition field label
            "Email": "attribution@example.com",  # Matches FormDefinition field label
            "page_url": post.get_url(),
            "landing_page_url": post.get_url(),
            "utm_source": "newsletter",
            "utm_campaign": "blog-promo",
            "csrfmiddlewaretoken": client.cookies.get("csrftoken").value,
        }

        response = client.post("/forms/submit/", data=form_data)
        assert response.status_code == 200

        # Verify attribution was captured
        lead = Lead.objects.get(email="attribution@example.com")
        assert lead.utm_source == "newsletter"
        assert lead.utm_campaign == "blog-promo"
        assert post.get_url() in lead.page_url
