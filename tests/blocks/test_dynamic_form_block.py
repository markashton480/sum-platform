from __future__ import annotations

import pytest
from bs4 import BeautifulSoup
from django.test import Client, RequestFactory
from home.models import HomePage
from sum_core.blocks.base import PageStreamBlock
from sum_core.blocks.forms import DynamicFormBlock
from sum_core.forms.models import ActiveFormDefinitionChooseView, FormDefinition
from sum_core.pages.models import StandardPage
from wagtail.models import Page, Site

pytestmark = pytest.mark.django_db


def _create_form_definition(site: Site, name: str = "CTA Form") -> FormDefinition:
    return FormDefinition.objects.create(
        site=site, name=name, slug=name.lower().replace(" ", "-")
    )


def _create_standard_page_with_dynamic_form(
    site: Site, form_definition: FormDefinition
) -> Page:
    homepage = HomePage.objects.first()
    if homepage is None:
        root = Page.get_first_root_node()
        homepage = HomePage(title="Theme Home", slug="theme-home")
        root.add_child(instance=homepage)

    site.root_page = homepage
    site.save()
    Site.clear_site_root_paths_cache()

    page = StandardPage(title="Dynamic Form Test", slug="dynamic-form-test")
    page.body = [
        (
            "dynamic_form",
            {
                "form_definition": form_definition,
                "presentation_style": "modal",
                "cta_button_text": "Launch form",
                "success_redirect_url": "https://example.com/thanks",
            },
        )
    ]
    homepage.add_child(instance=page)
    page.save_revision().publish()
    return page


class TestDynamicFormBlock:
    def test_block_definitions(self) -> None:
        block = DynamicFormBlock()
        fields = block.child_blocks

        assert set(fields.keys()) == {
            "form_definition",
            "presentation_style",
            "cta_button_text",
            "success_redirect_url",
        }

        style_choices = list(fields["presentation_style"].field.choices)
        assert ("inline", "Inline (renders in page flow)") in style_choices
        assert ("modal", "Modal (button opens overlay)") in style_choices
        assert ("sidebar", "Sidebar (fixed slide-in)") in style_choices
        assert block.meta.template == "sum_core/blocks/dynamic_form_block.html"
        assert block.meta.label == "Dynamic Form"

    def test_block_in_pagestreamblock(self) -> None:
        stream_block = PageStreamBlock()
        assert "dynamic_form" in stream_block.child_blocks
        assert isinstance(stream_block.child_blocks["dynamic_form"], DynamicFormBlock)

    def test_optional_fields_are_allowed(self, wagtail_default_site: Site) -> None:
        form_definition = _create_form_definition(wagtail_default_site)
        block = DynamicFormBlock()
        value = block.clean(
            {
                "form_definition": form_definition,
                "presentation_style": "inline",
                "cta_button_text": "",
                "success_redirect_url": "",
            }
        )
        assert value["cta_button_text"] == ""
        assert value["success_redirect_url"] == ""

    def test_only_active_forms_visible_in_chooser(
        self, wagtail_default_site: Site, rf: RequestFactory
    ) -> None:
        active_form = _create_form_definition(wagtail_default_site, name="Active Form")
        inactive_form = _create_form_definition(
            wagtail_default_site, name="Inactive Form"
        )
        inactive_form.is_active = False
        inactive_form.save(update_fields=["is_active"])

        request = rf.get("/", HTTP_HOST=wagtail_default_site.hostname)
        request.site = wagtail_default_site

        view = ActiveFormDefinitionChooseView()
        view.request = request
        view.model = FormDefinition

        chooser_qs = view.get_object_list()
        slugs = set(chooser_qs.values_list("slug", flat=True))

        assert active_form.slug in slugs
        assert inactive_form.slug not in slugs

    def test_block_renders_placeholder_template(
        self,
        client: Client,
        theme_active_copy,
        wagtail_default_site: Site,
    ) -> None:
        form_definition = _create_form_definition(wagtail_default_site)
        page = _create_standard_page_with_dynamic_form(
            wagtail_default_site, form_definition
        )

        response = client.get(page.url)
        assert response.status_code == 200

        templates = getattr(response, "templates", [])
        template_names = [t.name for t in templates if hasattr(t, "name")]
        assert "sum_core/blocks/dynamic_form_block.html" in template_names

        origin_paths = [
            str(getattr(template.origin, "name", ""))
            for template in templates
            if getattr(template, "name", None)
            == "sum_core/blocks/dynamic_form_block.html"
        ]
        assert any(
            "themes/theme_a/templates" in path or str(theme_active_copy) in path
            for path in origin_paths
        )

        soup = BeautifulSoup(response.content.decode("utf-8"), "html.parser")
        block_el = soup.select_one(".dynamic-form-wrapper")
        assert block_el is not None
        assert block_el.get("data-presentation") == "modal"
        assert "Launch form" in block_el.text
        assert "CTA Form" in block_el.text

    def test_chooser_filters_to_current_site(
        self, wagtail_default_site: Site, rf: RequestFactory
    ) -> None:
        other_home = HomePage(title="Alt Home", slug="alt-home")
        root = Page.get_first_root_node()
        root.add_child(instance=other_home)
        other_site = Site.objects.create(
            hostname="alt.test", root_page=other_home, is_default_site=False
        )
        Site.clear_site_root_paths_cache()

        site_form = _create_form_definition(wagtail_default_site, name="Site Form")
        _create_form_definition(other_site, name="Other Site Form")

        request = rf.get("/", HTTP_HOST=wagtail_default_site.hostname)
        request.site = wagtail_default_site

        view = ActiveFormDefinitionChooseView()
        view.request = request
        view.model = FormDefinition

        queryset = view.get_object_list()
        slugs = set(queryset.values_list("slug", flat=True))

        assert site_form.slug in slugs
        assert "other-site-form" not in slugs
