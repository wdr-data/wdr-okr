"""Base classes for admin forms."""

from django.contrib import admin


class ProductAdmin(admin.ModelAdmin):
    """Base class for products."""

    list_display = ["name"]
    list_display_links = ["name"]
    list_filter = ["is_active"]
    search_fields = ["name"]
    date_hierarchy = None


class QuintlyAdmin(ProductAdmin):
    """Base class for Quintly-related products."""

    list_display = ["name", "quintly_profile_id"]
