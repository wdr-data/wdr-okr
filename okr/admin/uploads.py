"""Basic form for file uploads."""

from typing import Dict, IO, List
from zipfile import ZipFile
import logging

from django import forms
from django.contrib import messages
from django.contrib.admin import helpers
from django.http import HttpResponseForbidden
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.urls import path
from django.urls.resolvers import URLResolver
from sentry_sdk import capture_exception


class UploadFileForm(forms.Form):
    uploaded_file = forms.FileField(label="Datei auswählen")


class UploadFileMixin:
    """
    Mixin for ModelAdmins to allow file uploads from the change list.
    Requires the ``process_uploaded_file(self, request: HttpRequest, file: UploadedFile)`` method
    to be implemented and the attribute ``upload_form_class`` must be set on the class.
    """

    change_list_template = "admin/okr/change_list_upload.html"
    upload_form_class = UploadFileForm

    def get_urls(self) -> List[URLResolver]:
        """Overrides ``admin.ModelAdmin`` to register the file upload endpoint."""
        return [
            path("upload-file/", self._upload_file),
        ] + super().get_urls()

    def open_zip(self, zip_file: IO[bytes]) -> Dict[str, IO[bytes]]:
        """Helper method to open an uploaded ZIP file.

        Args:
            zip_file (IO[bytes]): The uploaded ZIP file

        Returns:
            Dict[str, IO[bytes]]: A mapping from filename to file-like object of the zipped files
        """
        data_zip = ZipFile(zip_file)
        return {name: data_zip.open(name) for name in data_zip.namelist()}

    def _upload_file(self, request: HttpRequest) -> HttpResponse:
        if not self.has_add_permission(request):
            if not request.user.is_authenticated:
                return redirect("/admin/login")
            return HttpResponseForbidden()

        if request.method == "POST":
            try:
                uploaded_file = request.FILES["uploaded_file"]
            except KeyError:
                self.message_user(
                    request,
                    "Bitte eine Datei auswählen",
                    level=messages.ERROR,
                )
                return redirect(".")

            try:
                self.process_uploaded_file(request, uploaded_file)
            except Exception as e:
                capture_exception(e)
                logging.exception("Processing file upload failed")
                self.message_user(
                    request,
                    "Bei der Verarbeitung ist ein unerwarteter Fehler aufgetreten",
                    level=messages.ERROR,
                )

            return redirect("..")

        form = self.upload_form_class()

        admin_form = helpers.AdminForm(
            form,
            [(None, {"fields": form.fields})],
            {},
            [],
            model_admin=self,
        )

        opts = self.model._meta
        context = {
            "adminform": admin_form,
            "add": True,
            "change": False,
            "has_add_permission": self.has_add_permission(request),
            "has_file_field": True,
            "has_absolute_url": False,
            "opts": opts,
            "app_label": opts.app_label,
        }

        return render(request, "admin/okr/upload_form.html", context)
