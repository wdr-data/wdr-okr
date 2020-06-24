from django.urls import path

from . import views

urlpatterns = [
    path("triggers/insta/insights/<str:interval>/", views.insta.trigger_insights),
    path("triggers/insta/stories/", views.insta.trigger_stories),
    path("triggers/insta/posts/", views.insta.trigger_posts),
]
