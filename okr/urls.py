from django.urls import path

from . import views

urlpatterns = [
    path("triggers/insta/", views.insta.trigger),
]
