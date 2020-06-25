from zipfile import ZipFile

from django import forms
from django.contrib import admin
from django.contrib import messages
from django.contrib.admin import helpers
from django.core.exceptions import ValidationError
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.urls import path


class UploadFileForm(forms.Form):
    uploaded_file = forms.FileField()


class UploadFileMixin:
    """
    Mixin for ModelAdmins to allow file uploads from the change list.
    Requires the 'process_uploaded_file(self, request, file)' method to be implemented
    and the attribute 'upload_form_class' must be set on the class.
    """

    change_list_template = "admin/okr/change_list_upload.html"
    upload_form_class = UploadFileForm

    def get_urls(self):
        return [path("upload-file/", self._upload_file),] + super().get_urls()

    def open_zip(self, zip_file):
        data_zip = ZipFile(zip_file)
        return {name: data_zip.open(name) for name in data_zip.namelist()}

    def _upload_file(self, request):
        if not self.has_add_permission(request):
            if not request.user.is_authenticated:
                return redirect('/admin/login')
            return HttpResponseForbidden()

        if request.method == "POST":
            try:
                uploaded_file = request.FILES["uploaded_file"]
            except KeyError:
                self.message_user(
                    request, "Bitte eine Datei auswählen", level=messages.ERROR,
                )
                return redirect(".")

            try:
                self.process_uploaded_file(request, uploaded_file)
            except:
                self.message_user(
                    request,
                    "Bei der Verarbeitung ist ein unerwarteter Fehler aufgetreten",
                    level=messages.ERROR,
                )
            return redirect("..")

        form = self.upload_form_class()

        admin_form = helpers.AdminForm(
            form, [(None, {"fields": form.fields})], {}, [], model_admin=self,
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
