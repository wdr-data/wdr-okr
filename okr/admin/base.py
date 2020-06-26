from django.contrib import admin


class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "quintly_profile_id"]
    list_display_links = ["name"]
    list_filter = []
    date_hierarchy = None
