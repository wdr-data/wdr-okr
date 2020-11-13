from django import forms
from django.contrib import admin
from ..models import (
    Property,
    Page,
    PageMeta,
    PageDataGSC,
)
from .base import ProductAdmin


class PropertyAdmin(ProductAdmin):
    list_display = ProductAdmin.list_display + ["url"]


class PageAdmin(admin.ModelAdmin):
    list_display = [
        "property",
        "url",
        "sophora_id",
        "first_seen",
    ]
    list_display_links = ["url"]
    list_filter = ["property"]
    date_hierarchy = "first_seen"


class PageMetaAdmin(admin.ModelAdmin):
    list_display = [
        "headline",
        "editorial_update",
    ]
    list_display_links = ["headline"]
    date_hierarchy = "editorial_update"


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


admin.site.register(Property, PropertyAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(PageMeta, PageMetaAdmin)
admin.site.register(PageDataGSC, PageDataGCSAdmin)
