from django.contrib import admin

from ..models import YouTube, YouTubeAnalytics, YouTubeTrafficSource
from .uploads import UploadFileMixin


class TrafficSourceAdmin(UploadFileMixin, admin.ModelAdmin):
    def process_uploaded_file(self, request, file):
        self.message_user(request, "Datei wurde erfolgreich hochgeladen!")
        print(file.read())


admin.site.register(YouTube)
admin.site.register(YouTubeAnalytics)
admin.site.register(YouTubeTrafficSource, TrafficSourceAdmin)
