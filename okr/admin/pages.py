from okr.models.pages import (
    SophoraDocument,
    SophoraDocumentMeta,
    SophoraID,
    SophoraNode,
)
from django.contrib import admin
from ..models import (
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
        "first_seen",
    ]
    list_display_links = ["url"]
    list_filter = ["property"]
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


admin.site.register(Property, PropertyAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(SophoraNode, SophoraNodeAdmin)
admin.site.register(SophoraDocument, SophoraDocumentAdmin)
admin.site.register(SophoraID, SophoraIDAdmin)
admin.site.register(SophoraDocumentMeta, SophoraDocumentMetaAdmin)
admin.site.register(PageDataGSC, PageDataGCSAdmin)
