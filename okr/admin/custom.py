"""Forms for managing custom key result data."""

import json

from django.contrib import admin
from django.http.response import HttpResponse

from .mixins import UnrequiredFieldsMixin
from ..models import (
    CustomKeyResult,
    CustomKeyResultRecord,
)


class CustomKeyResultAdmin(admin.ModelAdmin):
    """List for choosing an existing custom key result to edit."""

    list_display = [
        "product_type",
        "product_name",
        "key_result",
        "key_result_type",
    ]
    list_filter = [
        "product_type",
        "key_result_type",
    ]

    list_display_links = [
        "product_type",
        "product_name",
        "key_result",
    ]


class CustomKeyResultRecordAdmin(UnrequiredFieldsMixin, admin.ModelAdmin):
    """List for choosing an existing key result record to edit."""

    change_form_template = "admin/okr/change_form_custom_key_results.html"

    list_display = [
        "key_result",
        "date",
        "value_integer",
        "value_text",
    ]

    list_filter = [
        "key_result",
    ]

    list_display_links = [
        "key_result",
        "date",
    ]

    unrequired_fields = [
        "value_text",
        "value_integer",
    ]

    def _create_json_data(self):
        key_results = CustomKeyResult.objects.all()
        json_data = {}
        for key_result in key_results:
            json_data[key_result.id] = key_result.key_result_type
        return json.dumps(json_data)

    def _update_extra_context(self, kwargs):
        extra_context = kwargs.get("extra_context", {})
        extra_context["key_result_types"] = self._create_json_data()
        kwargs["extra_context"] = extra_context

    def add_view(self, *args, **kwargs) -> HttpResponse:
        """ Add JSON data to add view for client-side JS. """
        self._update_extra_context(kwargs)
        return super().add_view(*args, **kwargs)

    def change_view(self, *args, **kwargs) -> HttpResponse:
        """ Add JSON data to change view for client-side JS. """
        self._update_extra_context(kwargs)
        return super().change_view(*args, **kwargs)


admin.site.register(CustomKeyResult, CustomKeyResultAdmin)
admin.site.register(CustomKeyResultRecord, CustomKeyResultRecordAdmin)
