"""Forms for managing custom key result data."""

import functools

from django import forms
from django.contrib import admin
from django.db import models

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

    list_display = [
        "key_result",
        "date",
        "value_number",
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
        "value_number",
    ]


admin.site.register(CustomKeyResult, CustomKeyResultAdmin)
admin.site.register(CustomKeyResultRecord, CustomKeyResultRecordAdmin)
