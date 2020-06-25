from django import forms
from django.contrib import admin
from django.contrib.admin import helpers
from django.shortcuts import render, redirect
from django.urls import path


class UploadFileForm(forms.Form):
    uploaded_file = forms.FileField()


class UploadFileMixin:
    """
    Mixin for ModelAdmins to allow file uploads from the change list.
    Requires the 'process_uploaded_file(self, request, file)' method to be implemented
    on the class.
    """

    change_list_template = "admin/okr/change_list_upload.html"

    def get_urls(self):
        return [path("upload-file/", self._upload_file),] + super().get_urls()

    def _upload_file(self, request):
        if request.method == "POST":
            uploaded_file = request.FILES["uploaded_file"]
            self.process_uploaded_file(request, uploaded_file)
            return redirect("..")

        form = UploadFileForm()

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
