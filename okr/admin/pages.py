from django.contrib import admin

from okr.models.pages import (
    SophoraDocument,
    SophoraDocumentMeta,
    SophoraID,
    SophoraNode,
    PageWebtrekkMeta,
    PageDataWebtrekk,
    Property,
    Page,
    PageDataGSC,
)
from .base import ProductAdmin


class PropertyAdmin(ProductAdmin):
    list_display = ProductAdmin.list_display + ["url"]


class PageAdmin(admin.ModelAdmin):
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


class PageDataGCSAdmin(admin.ModelAdmin):
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
    list_filter = []
    date_hierarchy = "date"


class SophoraNodeAdmin(admin.ModelAdmin):
    list_display = [
        "node",
        "use_exact_search",
    ]
    list_display_links = ["node"]


class SophoraDocumentAdmin(admin.ModelAdmin):
    list_display = [
        "export_uuid",
        "sophora_node",
    ]
    list_display_links = ["export_uuid"]
    date_hierarchy = "created"


class SophoraIDAdmin(admin.ModelAdmin):
    list_display = [
        "sophora_id",
        "sophora_document",
    ]
    list_display_links = ["sophora_id"]
    date_hierarchy = "created"


class SophoraDocumentMetaAdmin(admin.ModelAdmin):
    list_display = [
        "headline",
        "editorial_update",
        "node",
        "sophora_id",
        "document_type",
    ]
    list_display_links = ["headline"]
    list_filter = ["node", "document_type"]
    date_hierarchy = "editorial_update"


class PageWebtrekkMetaAdmin(admin.ModelAdmin):
    list_display = [
        "page",
        "headline",
        "query",
    ]
    list_display_links = ["headline"]
    list_filter = []
    date_hierarchy = "created"


class PageDataWebtrekkAdmin(admin.ModelAdmin):
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


admin.site.register(Property, PropertyAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(SophoraNode, SophoraNodeAdmin)
admin.site.register(SophoraDocument, SophoraDocumentAdmin)
admin.site.register(SophoraID, SophoraIDAdmin)
admin.site.register(SophoraDocumentMeta, SophoraDocumentMetaAdmin)
admin.site.register(PageDataGSC, PageDataGCSAdmin)
admin.site.register(PageWebtrekkMeta, PageWebtrekkMetaAdmin)
admin.site.register(PageDataWebtrekk, PageDataWebtrekkAdmin)
