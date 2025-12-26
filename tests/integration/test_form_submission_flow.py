"""
End-to-end form submission flow integration tests.

Tests the complete user journey from page load through form fill
to submission and Lead creation, including all side effects.
"""

from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.core.cache import cache
from sum_core.forms.models import FormConfiguration, FormDefinition
from sum_core.leads.models import EmailStatus, Lead
from sum_core.pages.blog import BlogIndexPage, BlogPostPage, Category
from sum_core.pages.models import StandardPage
from wagtail.models import Site

User = get_user_model()


@pytest.mark.django_db
class TestEndToEndFormSubmissionFlow:
    """Test complete form submission workflow from page load to Lead creation."""

    @pytest.fixture
    def site(self):
        """Get the default test site."""
        return Site.objects.get(is_default_site=True)

    @pytest.fixture
    def form_definition(self, site):
        """Create a standard contact form."""
        return FormDefinition.objects.create(
            name="Contact Form",
            slug="contact",
            site=site,
            fields=[
                (
                    "text_input",
                    {"field_name": "name", "label": "Full Name", "required": True},
                ),
                (
                    "email_input",
                    {
                        "field_name": "email",
                        "label": "Email Address",
                        "required": True,
                    },
                ),
                (
                    "phone_input",
                    {
                        "field_name": "phone",
                        "label": "Phone Number",
                        "required": False,
                    },
                ),
                (
                    "textarea",
                    {
                        "field_name": "message",
                        "label": "Your Message",
                        "required": True,
                        "rows": 5,
                    },
                ),
            ],
            success_message="Thank you for contacting us! We'll be in touch soon.",
            email_notification_enabled=True,
            notification_emails="admin@example.com",
            auto_reply_enabled=True,
            auto_reply_subject="Thanks for reaching out!",
            auto_reply_body="We received your message and will respond within 24 hours.",
            is_active=True,
        )

    @pytest.fixture
    def contact_page(self, site, form_definition):
        """Create a contact page with form."""
        home = site.root_page
        page = StandardPage(
            title="Contact Us",
            slug="contact",
            body=[
                (
                    "rich_text",
                    "<h2>Get in Touch</h2><p>We'd love to hear from you. Fill out the form below.</p>",
                ),
                (
                    "dynamic_form",
                    {
                        "form_definition": form_definition,
                        "presentation_style": "inline",
                        "cta_button_text": "Send Message",
                    },
                ),
            ],
        )
        home.add_child(instance=page)
        page.save_revision().publish()
        return page

    def test_complete_submission_flow_standard_page(
        self, client, contact_page, form_definition
    ):
        """Test end-to-end: load page → fill form → submit → Lead created."""
        # Step 1: User loads the contact page
        response = client.get(contact_page.get_url())
        assert response.status_code == 200
        content = response.content.decode()

        # Verify form is rendered
        assert "Contact Us" in content
        assert "Submit" in content

        # Step 2: User fills out and submits the form
        form_data = {
            "form_definition_id": form_definition.id,
            "name": "Jane Doe",
            "email": "jane@example.com",
            "phone": "555-1234",
            "message": "I'd like to learn more about your services.",
            "page_url": contact_page.get_url(),
            "landing_page_url": contact_page.get_url(),
            "csrfmiddlewaretoken": client.cookies.get("csrftoken").value,
        }

        submission_response = client.post("/forms/submit/", data=form_data)

        # Step 3: Verify successful submission response
        assert submission_response.status_code == 200
        response_data = submission_response.json()
        assert response_data["success"] is True
        assert "Thank you for contacting us" in response_data["message"]
        assert "lead_id" in response_data

        # Step 4: Verify Lead was created in database
        lead = Lead.objects.get(id=response_data["lead_id"])
        assert lead.name == "Jane Doe"
        assert lead.email == "jane@example.com"
        assert lead.phone == "555-1234"
        assert lead.message == "I'd like to learn more about your services."
        assert lead.form_type == form_definition.slug
        assert "ip_address" in lead.form_data
        assert lead.page_url == contact_page.get_url()
        assert lead.landing_page_url == contact_page.get_url()

    def test_submission_flow_with_attribution_tracking(
        self, client, contact_page, form_definition
    ):
        """Test that attribution data is captured throughout the flow."""
        # Step 1: User arrives via marketing campaign
        utm_params = "?utm_source=google&utm_medium=cpc&utm_campaign=spring-2024"
        landing_url = f"{contact_page.get_url()}{utm_params}"

        response = client.get(landing_url)
        assert response.status_code == 200

        # Step 2: User submits form with attribution
        form_data = {
            "form_definition_id": form_definition.id,
            "name": "Marketing User",
            "email": "marketing@example.com",
            "message": "Interested in your services.",
            "page_url": landing_url,
            "landing_page_url": landing_url,
            "utm_source": "google",
            "utm_medium": "cpc",
            "utm_campaign": "spring-2024",
            "referrer_url": "https://www.google.com/search",
            "csrfmiddlewaretoken": client.cookies.get("csrftoken").value,
        }

        submission_response = client.post("/forms/submit/", data=form_data)
        assert submission_response.status_code == 200

        # Step 3: Verify attribution was stored
        lead = Lead.objects.get(email="marketing@example.com")
        assert lead.utm_source == "google"
        assert lead.utm_medium == "cpc"
        assert lead.utm_campaign == "spring-2024"
        assert lead.referrer_url == "https://www.google.com/search"
        assert lead.lead_source == "google_ads"

    def test_submission_flow_with_success_message_display(
        self, client, contact_page, form_definition
    ):
        """Test that success message is properly returned and can be displayed."""
        response = client.get(contact_page.get_url())
        assert response.status_code == 200

        form_data = {
            "form_definition_id": form_definition.id,
            "name": "Success User",
            "email": "success@example.com",
            "message": "Test message.",
            "page_url": contact_page.get_url(),
            "landing_page_url": contact_page.get_url(),
            "csrfmiddlewaretoken": client.cookies.get("csrftoken").value,
        }

        submission_response = client.post("/forms/submit/", data=form_data)
        response_data = submission_response.json()

        # Verify custom success message is returned
        assert response_data["success"] is True
        assert response_data["message"] == form_definition.success_message
        assert "We'll be in touch soon" in response_data["message"]

    def test_submission_flow_with_redirect(self, client, site, form_definition):
        """Test submission flow with success redirect URL."""
        home = site.root_page

        # Create thank you page
        thank_you_page = StandardPage(
            title="Thank You",
            slug="thank-you",
            body=[
                (
                    "rich_text",
                    "<h2>Thanks for Contacting Us!</h2><p>We appreciate your interest and will respond soon.</p>",
                ),
            ],
        )
        home.add_child(instance=thank_you_page)
        thank_you_page.save_revision().publish()

        # Create page with form that redirects
        contact_page = StandardPage(
            title="Contact",
            slug="contact-redirect",
            body=[
                (
                    "dynamic_form",
                    {
                        "form_definition": form_definition,
                        "presentation_style": "inline",
                        "success_redirect_url": thank_you_page.get_url(),
                    },
                ),
            ],
        )
        home.add_child(instance=contact_page)
        contact_page.save_revision().publish()

        # Submit form
        response = client.get(contact_page.get_url())
        assert response.status_code == 200
        content = response.content.decode()
        assert f'data-success-redirect="{thank_you_page.get_url()}"' in content

        form_data = {
            "form_definition_id": form_definition.id,
            "name": "Redirect User",
            "email": "redirect@example.com",
            "message": "Test redirect.",
            "page_url": contact_page.get_url(),
            "landing_page_url": contact_page.get_url(),
            "csrfmiddlewaretoken": client.cookies.get("csrftoken").value,
        }

        submission_response = client.post("/forms/submit/", data=form_data)
        response_data = submission_response.json()

        # Verify successful submission response
        assert response_data["success"] is True

    def test_submission_flow_validation_errors(
        self, client, contact_page, form_definition
    ):
        """Test that validation errors are properly returned in the flow."""
        client.get(contact_page.get_url())

        # Submit with missing required fields
        form_data = {
            "form_definition_id": form_definition.id,
            "name": "",  # Required but empty
            "email": "invalid-email",  # Invalid format
            "message": "",  # Required but empty
            "page_url": contact_page.get_url(),
            "landing_page_url": contact_page.get_url(),
            "csrfmiddlewaretoken": client.cookies.get("csrftoken").value,
        }

        submission_response = client.post("/forms/submit/", data=form_data)
        assert submission_response.status_code == 400

        response_data = submission_response.json()
        assert response_data["success"] is False
        assert "errors" in response_data

        # Verify no Lead was created
        assert Lead.objects.filter(email="invalid-email").count() == 0


@pytest.mark.django_db
class TestBlogPostSubmissionFlow:
    """Test end-to-end submission flow from blog posts."""

    @pytest.fixture
    def blog_setup(self, db):
        """Create blog structure with form."""
        site = Site.objects.get(is_default_site=True)
        home = site.root_page

        blog_index = BlogIndexPage(title="Blog", slug="blog", posts_per_page=10)
        home.add_child(instance=blog_index)
        blog_index.save_revision().publish()

        category = Category.objects.create(name="Newsletter", slug="newsletter")

        form = FormDefinition.objects.create(
            name="Blog Newsletter",
            slug="blog-newsletter",
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
            success_message="You're subscribed to our newsletter!",
            is_active=True,
        )

        post = BlogPostPage(
            title="Subscribe to Our Newsletter",
            slug="subscribe-newsletter",
            excerpt="Stay updated with our latest content.",
            body=[
                ("rich_text", "<p>" + "Join our community! " * 50 + "</p>"),
                (
                    "dynamic_form",
                    {
                        "form_definition": form,
                        "presentation_style": "inline",
                        "cta_button_text": "Subscribe",
                    },
                ),
            ],
            category=category,
        )
        blog_index.add_child(instance=post)
        post.save_revision().publish()

        return {
            "site": site,
            "blog_index": blog_index,
            "post": post,
            "form": form,
            "category": category,
        }

    def test_blog_post_submission_complete_flow(self, client, blog_setup):
        """Test complete submission flow from blog post page."""
        post = blog_setup["post"]
        form = blog_setup["form"]

        # Step 1: Load blog post
        response = client.get(post.get_url())
        assert response.status_code == 200
        content = response.content.decode()
        assert "Subscribe" in content

        # Step 2: Submit newsletter form
        form_data = {
            "form_definition_id": form.id,
            "name": "Newsletter Subscriber",
            "email": "subscriber@example.com",
            "message": "Please subscribe me.",
            "page_url": post.get_url(),
            "landing_page_url": post.get_url(),
            "csrfmiddlewaretoken": client.cookies.get("csrftoken").value,
        }

        submission_response = client.post("/forms/submit/", data=form_data)
        assert submission_response.status_code == 200

        response_data = submission_response.json()
        assert response_data["success"] is True
        assert "subscribed" in response_data["message"].lower()

        # Step 3: Verify Lead created with blog post context
        lead = Lead.objects.get(email="subscriber@example.com")
        assert lead.name == "Newsletter Subscriber"
        assert lead.form_type == form.slug
        assert "ip_address" in lead.form_data
        assert post.get_url() in lead.page_url


@pytest.mark.django_db
class TestFormSubmissionWithSpamProtection:
    """Test submission flow with spam protection enabled."""

    @pytest.fixture
    def protected_form(self, db):
        """Create form with spam protection."""
        site = Site.objects.get(is_default_site=True)
        home = site.root_page

        form = FormDefinition.objects.create(
            name="Protected Form",
            slug="protected",
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
            title="Protected Contact",
            slug="protected-contact",
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

        return {"form": form, "page": page}

    def test_submission_flow_blocked_by_honeypot(self, client, protected_form):
        """Test that honeypot detection blocks spam submissions."""
        page = protected_form["page"]

        client.get(page.get_url())

        # Submit with honeypot filled (spam indicator)
        form_data = {
            "form_definition_id": protected_form["form"].id,
            "name": "Spammer",
            "email": "spam@example.com",
            "message": "Spam attempt",
            "website": "http://spam.com",  # Honeypot field
            "page_url": page.get_url(),
            "landing_page_url": page.get_url(),
            "csrfmiddlewaretoken": client.cookies.get("csrftoken").value,
        }

        submission_response = client.post("/forms/submit/", data=form_data)
        assert submission_response.status_code == 400

        response_data = submission_response.json()
        assert response_data["success"] is False

        # Verify no Lead was created
        assert Lead.objects.filter(email="spam@example.com").count() == 0

    def test_submission_flow_passes_spam_checks(self, client, protected_form):
        """Test that legitimate submissions pass spam protection."""
        page = protected_form["page"]

        client.get(page.get_url())

        # Submit without triggering spam protection
        form_data = {
            "form_definition_id": protected_form["form"].id,
            "name": "Legitimate User",
            "email": "legitimate@example.com",
            "message": "Legitimate inquiry",
            "page_url": page.get_url(),
            "landing_page_url": page.get_url(),
            "csrfmiddlewaretoken": client.cookies.get("csrftoken").value,
        }

        submission_response = client.post("/forms/submit/", data=form_data)
        assert submission_response.status_code == 200

        response_data = submission_response.json()
        assert response_data["success"] is True

        # Verify Lead was created
        lead = Lead.objects.get(email="legitimate@example.com")
        assert lead.name == "Legitimate User"


@pytest.mark.django_db
class TestNoLostLeadsInvariant:
    """Test that the 'no lost leads' invariant holds in various scenarios."""

    @pytest.fixture
    def form_setup(self, db):
        """Create form for testing no lost leads."""
        site = Site.objects.get(is_default_site=True)
        home = site.root_page

        form = FormDefinition.objects.create(
            name="Critical Form",
            slug="critical",
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
            success_message="Saved!",
            email_notification_enabled=True,
            notification_emails="alerts@example.com",
            auto_reply_enabled=True,
            auto_reply_subject="Thanks!",
            auto_reply_body="We received your submission.",
            is_active=True,
        )

        page = StandardPage(
            title="Critical Page",
            slug="critical-page",
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

        return {"form": form, "page": page}

    def test_lead_saved_even_if_emails_fail(self, client, form_setup, settings):
        """Test that Lead is saved even if email notifications fail."""
        page = form_setup["page"]
        client.get(page.get_url())

        form_data = {
            "form_definition_id": form_setup["form"].id,
            "name": "No Lost Lead",
            "email": "nolost@example.com",
            "message": "Please follow up.",
            "page_url": page.get_url(),
            "landing_page_url": page.get_url(),
            "csrfmiddlewaretoken": client.cookies.get("csrftoken").value,
        }

        with patch(
            "sum_core.forms.tasks.send_form_notification.delay",
            side_effect=Exception("Celery broker unavailable"),
        ):
            with patch(
                "sum_core.forms.tasks.send_auto_reply.delay",
                return_value=None,
            ):
                submission_response = client.post("/forms/submit/", data=form_data)
                assert submission_response.status_code == 200

        # Verify Lead was created despite email failure
        lead = Lead.objects.get(email="nolost@example.com")
        assert lead.name == "No Lost Lead"
        lead.refresh_from_db()
        assert lead.form_notification_status == EmailStatus.FAILED

    def test_validation_errors_do_not_create_lead(self, client, form_setup):
        """Test that invalid submissions don't create partial Leads."""
        page = form_setup["page"]
        client.get(page.get_url())

        # Submit with validation errors
        form_data = {
            "form_definition_id": form_setup["form"].id,
            "name": "",  # Required but missing
            "email": "invalid",  # Invalid format
            "message": "",  # Required but missing
            "page_url": page.get_url(),
            "landing_page_url": page.get_url(),
            "csrfmiddlewaretoken": client.cookies.get("csrftoken").value,
        }

        submission_response = client.post("/forms/submit/", data=form_data)
        assert submission_response.status_code == 400

        # Verify no Lead was created
        assert Lead.objects.filter(email="invalid").count() == 0

    def test_lead_persisted_even_if_celery_task_fails(self, client, form_setup):
        """Test that Lead is persisted even if Celery task queuing fails.

        This tests the "No Lost Leads" invariant: the Lead must be saved to the
        database BEFORE any async tasks (email, webhook) are queued. If Celery
        is unavailable or the task fails to queue, the Lead should still exist.
        """
        page = form_setup["page"]
        client.get(page.get_url())

        form_data = {
            "form_definition_id": form_setup["form"].id,
            "name": "Celery Failure Test",
            "email": "celery-fail@example.com",
            "message": "Celery queue down.",
            "page_url": page.get_url(),
            "landing_page_url": page.get_url(),
            "csrfmiddlewaretoken": client.cookies.get("csrftoken").value,
        }

        with patch(
            "sum_core.forms.tasks.send_auto_reply.delay",
            side_effect=Exception("Celery broker unavailable"),
        ):
            with patch(
                "sum_core.forms.tasks.send_form_notification.delay",
                return_value=None,
            ):
                submission_response = client.post("/forms/submit/", data=form_data)
                assert submission_response.status_code == 200

        # Verify Lead was created despite Celery failure
        lead = Lead.objects.get(email="celery-fail@example.com")
        assert lead.name == "Celery Failure Test"
        lead.refresh_from_db()
        assert lead.auto_reply_status == EmailStatus.FAILED


@pytest.mark.django_db
class TestSecurityEdgeCases:
    """Test security edge cases for form submissions.

    These tests verify that malicious input is handled safely without
    causing SQL injection, path traversal, or other security issues.
    """

    @pytest.fixture
    def security_form_setup(self, db):
        """Create form for security testing."""
        site = Site.objects.get(is_default_site=True)
        home = site.root_page

        cache.clear()
        config = FormConfiguration.get_for_site(site)
        config.rate_limit_per_ip_per_hour = 0
        config.save(update_fields=["rate_limit_per_ip_per_hour"])

        form = FormDefinition.objects.create(
            name="Security Test Form",
            slug="security-test",
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
                    {
                        "field_name": "message",
                        "label": "Message",
                        "required": False,
                        "rows": 5,
                    },
                ),
            ],
            success_message="Saved!",
            is_active=True,
        )

        page = StandardPage(
            title="Security Test Page",
            slug="security-test-page",
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

        return {"form": form, "page": page}

    def test_sql_injection_in_form_fields(self, client, security_form_setup):
        """Test that SQL injection attempts are safely handled.

        Form data should be parameterized/escaped, never concatenated into SQL.
        """
        page = security_form_setup["page"]
        client.get(page.get_url())

        sql_injection_payloads = [
            "'; DROP TABLE leads;--",
            "1' OR '1'='1",
            "1; DELETE FROM leads WHERE 1=1;--",
            "Robert'); DROP TABLE leads;--",  # Bobby Tables
        ]

        for payload in sql_injection_payloads:
            form_data = {
                "form_definition_id": security_form_setup["form"].id,
                "name": payload,
                "email": "sqli-test@example.com",
                "message": payload,
                "page_url": page.get_url(),
                "landing_page_url": page.get_url(),
                "csrfmiddlewaretoken": client.cookies.get("csrftoken").value,
            }

            # Should succeed without SQL injection executing
            response = client.post("/forms/submit/", data=form_data)
            assert response.status_code == 200

            # Lead should be created with literal SQL payload as data
            lead = Lead.objects.filter(email="sqli-test@example.com").last()
            assert lead is not None
            assert payload in lead.name or payload in lead.message

            # Clean up for next iteration
            lead.delete()

    def test_path_traversal_in_form_fields(self, client, security_form_setup):
        """Test that path traversal attempts are safely handled.

        File paths in form data should not be used to access filesystem.
        """
        page = security_form_setup["page"]
        client.get(page.get_url())

        path_traversal_payloads = [
            "../../etc/passwd",
            "../../../etc/shadow",
            "..\\..\\windows\\system32\\config\\sam",
            "/etc/passwd",
            "file:///etc/passwd",
        ]

        for payload in path_traversal_payloads:
            form_data = {
                "form_definition_id": security_form_setup["form"].id,
                "name": payload,
                "email": "path-test@example.com",
                "message": payload,
                "page_url": page.get_url(),
                "landing_page_url": page.get_url(),
                "csrfmiddlewaretoken": client.cookies.get("csrftoken").value,
            }

            # Should succeed - path traversal should be stored as literal string
            response = client.post("/forms/submit/", data=form_data)
            assert response.status_code == 200

            # Lead should be created with literal path as data (no file access)
            lead = Lead.objects.filter(email="path-test@example.com").last()
            assert lead is not None
            assert payload in lead.name or payload in lead.message

            # Clean up for next iteration
            lead.delete()
