"""Forms for managing page data."""

from django.contrib import admin

from okr.models.pages import (
    SophoraDocument,
    SophoraDocumentMeta,
    SophoraID,
    SophoraNode,
    SophoraKeyword,
    PageWebtrekkMeta,
    PageDataWebtrekk,
    Property,
    Page,
    PageDataGSC,
    PageDataQueryGSC,
    PropertyDataGSC,
    PropertyDataQueryGSC,
)
from .base import ProductAdmin
from .mixins import large_table


class PropertyAdmin(ProductAdmin):
    """List for choosing basic product."""

    list_display = ProductAdmin.list_display + ["url"]


class PageAdmin(admin.ModelAdmin):
    """List for choosing existing page to edit."""

    list_display = [
        "property",
        "url",
        "sophora_document",
        "sophora_id",
        "node",
        "first_seen",
    ]
    list_display_links = ["url"]
    list_filter = ["property", "node"]
    date_hierarchy = "first_seen"
    search_fields = ["url"]


@large_table
class PropertyDataGSCAdmin(admin.ModelAdmin):
    """List for choosing existing GSC property data to edit."""

    list_display = [
        "property",
        "date",
        "device",
        "clicks",
        "impressions",
        "ctr",
        "position",
    ]
    list_display_links = ["property", "date"]
    list_filter = ["property"]
    date_hierarchy = "date"


@large_table
class PropertyDataQueryGSCAdmin(admin.ModelAdmin):
    """List for choosing existing GSC property query data to edit."""

    list_display = [
        "property",
        "date",
        "query",
        "clicks",
        "impressions",
        "ctr",
        "position",
    ]
    list_display_links = ["property", "date"]
    date_hierarchy = "date"
    search_fields = ["query"]


@large_table
class PageDataGSCAdmin(admin.ModelAdmin):
    """List for choosing existing GSC page data to edit."""

    list_display = [
        "page",
        "date",
        "device",
        "clicks",
        "impressions",
        "ctr",
        "position",
    ]
    list_display_links = ["page", "date"]
    list_filter = ["device"]
    date_hierarchy = "date"
    search_fields = ["page__url"]


@large_table
class PageDataQueryGSCAdmin(admin.ModelAdmin):
    """List for choosing existing GSC page query data to edit."""

    list_display = [
        "page",
        "date",
        "query",
        "clicks",
        "impressions",
        "ctr",
        "position",
    ]
    list_display_links = ["page", "date"]
    date_hierarchy = "date"
    search_fields = ["query"]


class SophoraNodeAdmin(admin.ModelAdmin):
    """List for choosing existing Sophora nodes to edit."""

    list_display = [
        "node",
        "use_exact_search",
    ]
    list_display_links = ["node"]
    search_fields = ["node"]


class SophoraDocumentAdmin(admin.ModelAdmin):
    """List for choosing existing Sophora documents to edit."""

    list_display = [
        "export_uuid",
        "sophora_node",
    ]
    list_display_links = ["export_uuid"]
    date_hierarchy = "created"
    search_fields = ["export_uuid"]


class SophoraIDAdmin(admin.ModelAdmin):
    """List for choosing existing Sophora IDs to edit."""

    list_display = [
        "sophora_id",
        "sophora_document",
    ]
    list_display_links = ["sophora_id"]
    date_hierarchy = "created"
    search_fields = ["sophora_id"]


class SophoraDocumentMetaAdmin(admin.ModelAdmin):
    """List for choosing existing Sophora document meta data to edit."""

    list_display = [
        "headline",
        "created",
        "editorial_update",
        "node",
        "sophora_id",
        "document_type",
        "word_count",
    ]
    list_display_links = ["headline"]
    list_filter = ["node", "document_type"]
    date_hierarchy = "created"
    search_fields = ["headline", "keywords_list"]


class SophoraKeywordAdmin(admin.ModelAdmin):
    """List for choosing existing Sophora keywords to edit."""

    list_display = ["keyword", "first_seen"]
    list_display_links = ["keyword"]
    date_hierarchy = "first_seen"
    search_fields = ["keyword"]


class PageWebtrekkMetaAdmin(admin.ModelAdmin):
    """List for choosing existing Webtrekk meta data to edit."""

    list_display = [
        "page",
        "headline",
        "query",
    ]
    list_display_links = ["headline"]
    list_filter = []
    date_hierarchy = "created"
    search_fields = ["headline"]


@large_table
class PageDataWebtrekkAdmin(admin.ModelAdmin):
    """List for choosing existing Webtrekk data to edit."""

    list_display = [
        "webtrekk_meta",
        "date",
        "visits",
        "visits_search",
        "impressions",
        "impressions_search",
        "entries",
        "entries_search",
    ]
    list_display_links = ["webtrekk_meta", "date"]
    list_filter = []
    date_hierarchy = "date"
    search_fields = ["webtrekk_meta__headline"]


admin.site.register(Property, PropertyAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(SophoraNode, SophoraNodeAdmin)
admin.site.register(SophoraDocument, SophoraDocumentAdmin)
admin.site.register(SophoraID, SophoraIDAdmin)
admin.site.register(SophoraDocumentMeta, SophoraDocumentMetaAdmin)
admin.site.register(SophoraKeyword, SophoraKeywordAdmin)
admin.site.register(PropertyDataGSC, PropertyDataGSCAdmin)
admin.site.register(PropertyDataQueryGSC, PropertyDataQueryGSCAdmin)
admin.site.register(PageDataGSC, PageDataGSCAdmin)
admin.site.register(PageDataQueryGSC, PageDataQueryGSCAdmin)
admin.site.register(PageWebtrekkMeta, PageWebtrekkMetaAdmin)
admin.site.register(PageDataWebtrekk, PageDataWebtrekkAdmin)
