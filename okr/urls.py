from django.urls import path

from . import views

urlpatterns = [
    path("triggers/insta/<str:interval>", views.insta.trigger),
]
