from django import forms
from django.contrib import admin
from ..models import (
    Insta,
    InstaInsight,
    InstaPost,
    InstaStory,
    InstaCollaboration,
    InstaCollaborationType,
)
from .base import ProductAdmin


class CollaborationModelForm(forms.ModelForm):
    class Meta:
        model = InstaCollaboration
        exclude = ()

    def get_initial_for_field(self, field, field_name):
        if field_name == "insta" and not self.instance.id:
            instas = Insta.objects.all()[:1]
            instas = list(instas)
            if instas:
                return instas[0]

        return super().get_initial_for_field(field, field_name)


class CollaborationAdmin(admin.ModelAdmin):
    form = CollaborationModelForm
    list_display = ["time", "influencer", "collaboration_type", "followers"]
    list_display_links = ["influencer"]
    readonly_fields = ["last_updated"]


class InsightAdmin(admin.ModelAdmin):
    list_display = [
        "time",
        "insta",
        "interval",
        "reach",
        "impressions",
        "followers_change",
        "posts_change",
    ]
    list_display_links = ["time"]
    list_filter = ["insta", "interval"]
    date_hierarchy = "time"


class PostAdmin(admin.ModelAdmin):
    list_display = [
        "external_id",
        "insta",
        "time",
        "post_type",
        "likes",
        "reach",
        "impressions",
    ]
    list_display_links = ["external_id"]
    list_filter = ["insta", "post_type"]
    date_hierarchy = "time"


class StoryAdmin(admin.ModelAdmin):
    list_display = [
        "external_id",
        "insta",
        "time",
        "story_type",
        "reach",
        "impressions",
        "exits",
    ]
    list_display_links = ["external_id"]
    list_filter = ["insta", "story_type"]
    date_hierarchy = "time"


class CollaborationTypeAdmin(admin.ModelAdmin):
    list_display = [
        "name",
    ]
    list_display_links = ["name"]
    list_filter = []
    date_hierarchy = None


admin.site.register(Insta, ProductAdmin)
admin.site.register(InstaInsight, InsightAdmin)
admin.site.register(InstaPost, PostAdmin)
admin.site.register(InstaStory, StoryAdmin)
admin.site.register(InstaCollaboration, CollaborationAdmin)
admin.site.register(InstaCollaborationType)
