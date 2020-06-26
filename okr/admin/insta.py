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
    readonly_fields = ["last_updated"]


admin.site.register(Insta)
admin.site.register(InstaInsight)
admin.site.register(InstaPost)
admin.site.register(InstaStory)
admin.site.register(InstaCollaboration, CollaborationAdmin)
admin.site.register(InstaCollaborationType)
