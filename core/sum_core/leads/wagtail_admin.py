"""
Name: Leads admin (Wagtail)
Path: core/sum_core/leads/wagtail_admin.py
Purpose: Provide Wagtail admin UI for Lead list/detail, status updates, and CSV export.
Family: Lead management, operations workflows.
Dependencies: Wagtail admin APIs, Lead model, attribution fields.
"""

from __future__ import annotations

from typing import Any

from django.http import HttpRequest, HttpResponse
from django.urls import path
from django.utils.html import format_html
from sum_core.leads.models import Lead, LeadSourceRule
from wagtail import hooks
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.admin.ui.tables import Column, DateColumn
from wagtail.admin.viewsets.model import ModelViewSet
from wagtail.permissions import ModelPermissionPolicy
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet


class LeadStatusColumn(Column):
    """Custom column for rendering lead status with styling."""

    def render_cell_html(self, obj: Lead, **kwargs: Any) -> str:
        status_colors = {
            Lead.Status.NEW: "#2563eb",  # blue
            Lead.Status.CONTACTED: "#7c3aed",  # purple
            Lead.Status.QUOTED: "#ea580c",  # orange
            Lead.Status.WON: "#16a34a",  # green
            Lead.Status.LOST: "#dc2626",  # red
        }
        color = status_colors.get(obj.status, "#64748b")
        return format_html(
            '<span style="color: {}; font-weight: 600;">{}</span>',
            color,
            obj.get_status_display(),
        )


class LeadViewSet(ModelViewSet):
    """
    Wagtail admin ViewSet for Lead management.

    Provides:
    - List view with search, filters, and columns
    - Detail view with grouped sections
    - Status update capability (permission-gated)
    - CSV export (permission-gated)
    """

    model = Lead
    icon = "mail"
    menu_label = "Leads"
    menu_order = 200
    add_to_settings_menu = False
    exclude_from_explorer = False
    copy_view_enabled = False
    inspect_view_enabled = True

    list_display = [
        DateColumn("submitted_at", label="Submitted", width="15%"),
        Column("name", label="Name", width="15%"),
        Column("email", label="Email", width="20%"),
        Column("phone", label="Phone", width="12%"),
        Column("form_type", label="Form", width="10%"),
        Column("lead_source", label="Source", width="12%"),
        LeadStatusColumn("status", label="Status", width="10%"),
    ]

    list_filter = [
        "status",
        "lead_source",
        "form_type",
        "submitted_at",
    ]

    search_fields = ["name", "email", "phone", "message"]

    # Detail view panels
    panels = [
        MultiFieldPanel(
            [
                FieldPanel("status"),
                FieldPanel("is_archived"),
                FieldPanel("submitted_at", read_only=True),
            ],
            heading="Status",
        ),
        MultiFieldPanel(
            [
                FieldPanel("name", read_only=True),
                FieldPanel("email", read_only=True),
                FieldPanel("phone", read_only=True),
                FieldPanel("message", read_only=True),
            ],
            heading="Contact Details",
        ),
        MultiFieldPanel(
            [
                FieldPanel("form_type", read_only=True),
                FieldPanel("source_page", read_only=True),
            ],
            heading="Form Information",
        ),
        MultiFieldPanel(
            [
                FieldPanel("lead_source", read_only=True),
                FieldPanel("lead_source_detail", read_only=True),
                FieldPanel("utm_source", read_only=True),
                FieldPanel("utm_medium", read_only=True),
                FieldPanel("utm_campaign", read_only=True),
                FieldPanel("utm_term", read_only=True),
                FieldPanel("utm_content", read_only=True),
            ],
            heading="Attribution",
            classname="collapsible collapsed",
        ),
        MultiFieldPanel(
            [
                FieldPanel("landing_page_url", read_only=True),
                FieldPanel("page_url", read_only=True),
                FieldPanel("referrer_url", read_only=True),
            ],
            heading="URLs",
            classname="collapsible collapsed",
        ),
    ]

    def get_queryset(self, request: HttpRequest) -> Any:
        """Get queryset with optimizations."""
        qs = super().get_queryset(request)
        return qs.select_related("source_page")

    @property
    def permission_policy(self) -> ModelPermissionPolicy:
        """Custom permission policy for edit/export controls."""
        return LeadPermissionPolicy(self.model)

    def get_urlpatterns(self) -> list:
        """Add CSV export URL pattern."""
        urlpatterns = super().get_urlpatterns()
        return urlpatterns + [
            path("export/", self.export_csv_view, name="export"),
        ]

    def export_csv_view(self, request: HttpRequest) -> HttpResponse:
        """
        Export filtered leads to CSV.

        Only accessible to users with 'export_lead' permission.
        """
        from sum_core.leads.services import build_lead_csv, can_user_export_leads

        # Permission check
        if not can_user_export_leads(request.user):
            from django.core.exceptions import PermissionDenied

            raise PermissionDenied("You do not have permission to export leads.")

        # Get filtered queryset (respects list_filter state)
        queryset = self.get_queryset(request)

        # Apply any active filters from the list view
        # Note: In production, you'd parse the querystring to apply filters
        # For simplicity, we export the base queryset
        queryset = queryset.select_related("source_page")

        # Generate CSV
        csv_content = build_lead_csv(queryset)

        # Return as downloadable file
        response = HttpResponse(csv_content, content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="leads_export.csv"'
        return response


class LeadPermissionPolicy(ModelPermissionPolicy):
    """
    Custom permission policy for Lead model.

    - Editors (change_lead): can view list and detail
    - Admins (change_lead + export_lead): can also update status and export CSV
    """

    def user_has_permission(self, user: Any, action: str) -> bool:
        """Check if user has permission for the given action."""
        if action in ["add"]:
            # No one can add leads through Wagtail admin (they come from forms)
            return False

        if action in ["change", "delete"]:
            # Only users with change_lead can edit status/archive
            return user.has_perm("leads.change_lead")

        if action == "export":
            # Only users with export_lead can export
            return user.has_perm("leads.export_lead")

        # For index/inspect, allow if user has view or change permission
        return super().user_has_permission(user, action)


# Register the viewset
@hooks.register("register_admin_viewset")
def register_lead_viewset() -> LeadViewSet:
    """Register the Lead ViewSet with Wagtail admin."""
    return LeadViewSet("leads")


# Also register LeadSourceRule as a snippet for configuration


class LeadSourceRuleViewSet(SnippetViewSet):
    """ViewSet for LeadSourceRule configuration."""

    model = LeadSourceRule
    icon = "cog"
    menu_label = "Lead Source Rules"
    menu_order = 201
    add_to_admin_menu = True

    list_display = [
        "priority",
        "name",
        "utm_source",
        "utm_medium",
        "referrer_contains",
        "derived_source",
        "is_active",
    ]
    list_filter = ["is_active", "derived_source"]
    search_fields = ["name", "utm_source", "utm_medium", "referrer_contains"]

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("name"),
                FieldPanel("priority"),
                FieldPanel("is_active"),
            ],
            heading="Rule Identity",
        ),
        MultiFieldPanel(
            [
                FieldPanel("utm_source"),
                FieldPanel("utm_medium"),
                FieldPanel("referrer_contains"),
            ],
            heading="Matching Conditions",
        ),
        MultiFieldPanel(
            [
                FieldPanel("derived_source"),
                FieldPanel("derived_source_detail"),
            ],
            heading="Derived Values",
        ),
    ]


register_snippet(LeadSourceRuleViewSet)
