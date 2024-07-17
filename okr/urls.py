from django.urls import path

from .views import xlsx_service

urlpatterns = [
    path('xlsx/<str:id>', xlsx_service.generate_xlsx, name='xlsx_service'),
]
