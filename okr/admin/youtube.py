from django.contrib import admin
from ..models import YouTube, YouTubeAnalytics, YouTubeTrafficSource

class TrafficSourceAdmin(admin.ModelAdmin):
    change_list_template='admin/okr/change_list_upload.html'

admin.site.register(YouTube)
admin.site.register(YouTubeAnalytics)
admin.site.register(YouTubeTrafficSource, TrafficSourceAdmin)
